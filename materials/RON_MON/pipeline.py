import logging

import hydra
import mlflow
import mlflow.catboost
import mlflow.sklearn
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from omegaconf import DictConfig
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, rdFingerprintGenerator
from rdkit import DataStructs
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_selection import VarianceThreshold, mutual_info_regression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

log = logging.getLogger(__name__)


# ── Descriptors ──────────────────────────────────────────────────────────────


def compute_rdkit_2d(smiles_list: list[str]) -> pd.DataFrame:
    descriptor_names = [
        "MolWt", "MolLogP", "TPSA", "NumHAcceptors", "NumHDonors",
        "NumRotatableBonds", "NumAromaticRings", "NumAliphaticRings",
        "RingCount", "FractionCSP3", "HeavyAtomCount",
        "NumValenceElectrons", "BalabanJ", "BertzCT", "HallKierAlpha",
        "Kappa1", "Kappa2", "Kappa3",
        "Chi0v", "Chi1v", "Chi2v", "Chi3v",
        "LabuteASA", "PEOE_VSA1", "PEOE_VSA2",
        "SMR_VSA1", "SMR_VSA2", "SlogP_VSA1", "SlogP_VSA2",
        "MaxAbsEStateIndex", "MinAbsEStateIndex",
        "MaxAbsPartialCharge", "MinAbsPartialCharge",
    ]
    funcs = {n: getattr(Descriptors, n) for n in descriptor_names if hasattr(Descriptors, n)}
    records = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            records.append({n: np.nan for n in funcs})
        else:
            records.append({n: f(mol) for n, f in funcs.items()})
    return pd.DataFrame(records)


def compute_morgan(smiles_list: list[str], radius: int = 2, n_bits: int = 1024) -> pd.DataFrame:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            fps.append(np.zeros(n_bits, dtype=int))
            continue
        fps.append(gen.GetFingerprintAsNumPy(mol))
    return pd.DataFrame(fps, columns=[f"morgan_{i}" for i in range(n_bits)])


def compute_maccs(smiles_list: list[str]) -> pd.DataFrame:
    fps = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            fps.append(np.zeros(167))
            continue
        fp = rdMolDescriptors.GetMACCSKeysFingerprint(mol)
        arr = np.zeros(167, dtype=int)
        DataStructs.ConvertToNumpyArray(fp, arr)
        fps.append(arr)
    return pd.DataFrame(fps, columns=[f"maccs_{i}" for i in range(167)])


# ── Feature Selection ────────────────────────────────────────────────────────


def select_features(X: pd.DataFrame, y: np.ndarray, cfg: DictConfig) -> pd.DataFrame:
    # Low variance
    sel = VarianceThreshold(threshold=cfg.feature_selection.variance_threshold)
    sel.fit(X)
    X = X.loc[:, sel.get_support()]
    log.info("After variance filter: %d features", X.shape[1])

    # Correlation
    corr = X.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [c for c in upper.columns if any(upper[c] > cfg.feature_selection.correlation_threshold)]
    X = X.drop(columns=to_drop)
    log.info("After correlation filter: %d features", X.shape[1])

    # Mutual information
    if cfg.feature_selection.method == "mutual_info":
        mi = mutual_info_regression(X, y, random_state=42)
        mi_series = pd.Series(mi, index=X.columns).sort_values(ascending=False)
        n = min(cfg.feature_selection.n_features_to_select, len(mi_series))
        X = X[mi_series.head(n).index.tolist()]
        log.info("After MI selection: %d features", X.shape[1])

    return X


# ── Model Factory ────────────────────────────────────────────────────────────


def build_model(cfg: DictConfig):
    name = cfg.model.name
    if name == "catboost":
        return CatBoostRegressor(**cfg.model.catboost)
    elif name == "random_forest":
        return RandomForestRegressor(**cfg.model.random_forest)
    elif name == "gradient_boosting":
        return GradientBoostingRegressor(**cfg.model.gradient_boosting)
    else:
        raise ValueError(f"Unknown model: {name}")


# ── Main Pipeline ────────────────────────────────────────────────────────────


@hydra.main(config_path="configs", config_name="config", version_base=None)
def main(cfg: DictConfig):
    log.info("Target: %s, Model: %s", cfg.data.target, cfg.model.name)

    # Load data
    df = pd.read_csv(hydra.utils.to_absolute_path(cfg.data.path), encoding="utf-8-sig")
    df = df.dropna(subset=[cfg.data.target])
    smiles = df["Smiles"].tolist()
    y = df[cfg.data.target].values

    # Compute descriptors
    parts = []
    if cfg.descriptors.use_rdkit_2d:
        parts.append(compute_rdkit_2d(smiles))
    if cfg.descriptors.use_morgan_fp:
        parts.append(compute_morgan(smiles, cfg.descriptors.morgan_radius, cfg.descriptors.morgan_n_bits))
    if cfg.descriptors.use_maccs:
        parts.append(compute_maccs(smiles))

    X = pd.concat(parts, axis=1).fillna(0)
    log.info("Total descriptors: %d", X.shape[1])

    # Feature selection
    X = select_features(X, y, cfg)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X.values, y, test_size=cfg.data.test_size, random_state=cfg.data.random_state
    )

    # Scale (for non-tree models the scaler is applied; tree models are invariant)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    needs_scaling = cfg.model.name not in ("catboost", "random_forest", "gradient_boosting")
    X_tr = X_train_s if needs_scaling else X_train
    X_te = X_test_s if needs_scaling else X_test

    # Train
    model = build_model(cfg)
    model.fit(X_tr, y_train)
    y_pred = model.predict(X_te)

    # Metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = r2_score(y_test, y_pred)

    log.info("MAE=%.2f  RMSE=%.2f  R2=%.4f", mae, rmse, r2)

    # MLflow logging
    mlflow.set_tracking_uri(hydra.utils.to_absolute_path(cfg.mlflow.tracking_uri))
    mlflow.set_experiment(cfg.mlflow.experiment_name)

    with mlflow.start_run(run_name=f"{cfg.model.name}_{cfg.data.target}"):
        mlflow.log_param("model", cfg.model.name)
        mlflow.log_param("target", cfg.data.target)
        mlflow.log_param("n_features", X_tr.shape[1])
        mlflow.log_param("test_size", cfg.data.test_size)

        if cfg.model.name == "catboost":
            for k, v in cfg.model.catboost.items():
                mlflow.log_param(f"cb_{k}", v)

        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        if cfg.model.name == "catboost":
            mlflow.catboost.log_model(model, "model")
        else:
            mlflow.sklearn.log_model(model, "model")

    log.info("Run logged to MLflow experiment '%s'", cfg.mlflow.experiment_name)


if __name__ == "__main__":
    main()
