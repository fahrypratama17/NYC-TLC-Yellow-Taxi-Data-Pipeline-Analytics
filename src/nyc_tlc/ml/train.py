"""
* 245150201111042  ANINDHITA FAIZA AULIA
* 245150201111043  ANIZA HELWA MAHANANI
* 245150207111046  MUHAMAD FAHRY PRATAMA PUTRA
* 245150201111002  MUHAMMAD ATHA TSAQIF
* 245150200111008  NAFIS NAUFAL RAHMAN
* 245150200111061  RICHARD SAMUEL HATANE
"""

from __future__ import annotations

from nyc_tlc.ml.clustering import train_clustering
from nyc_tlc.utils import get_logger

log = get_logger(__name__)


def main() -> None:
    log.info("ml.train.start")
    result = train_clustering()
    log.info("ml.train.done", winner=result["winner"], k=result["n_clusters"])


if __name__ == "__main__":
    main()
