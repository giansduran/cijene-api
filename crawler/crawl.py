import os
import datetime
from typing import List
import logging
from pathlib import Path
from time import time


from crawler.store.konzum import KonzumCrawler
from crawler.store.lidl import LidlCrawler
from crawler.store.plodine import PlodineCrawler
from crawler.store.spar import SparCrawler
from crawler.store.studenac import StudenacCrawler
from crawler.store.tommy import TommyCrawler
from crawler.store.kaufland import KauflandCrawler
from crawler.store.eurospin import EurospinCrawler
from crawler.store.dm import DmCrawler
from crawler.store.ktc import KtcCrawler
from crawler.store.metro import MetroCrawler

from crawler.store.output import save_chain, copy_archive_info, create_archive

logger = logging.getLogger(__name__)

CRAWLERS = {
    StudenacCrawler.CHAIN: StudenacCrawler,
    SparCrawler.CHAIN: SparCrawler,
    KonzumCrawler.CHAIN: KonzumCrawler,
    PlodineCrawler.CHAIN: PlodineCrawler,
    LidlCrawler.CHAIN: LidlCrawler,
    TommyCrawler.CHAIN: TommyCrawler,
    KauflandCrawler.CHAIN: KauflandCrawler,
    EurospinCrawler.CHAIN: EurospinCrawler,
    DmCrawler.CHAIN: DmCrawler,
    KtcCrawler.CHAIN: KtcCrawler,
    MetroCrawler.CHAIN: MetroCrawler,
}


def get_chains() -> List[str]:
    """
    Get the list of retail chains from the crawlers.

    Returns:
        List of retail chain names.
    """
    return list(CRAWLERS.keys())


def crawl_chain(chain: str, date: datetime.date, path: Path):
    """
    Crawl a specific retail chain for product/pricing data and save it.

    Args:
        chain: The name of the retail chain to crawl.
        date: The date for which to fetch the product data.
        path: The directory path where the data will be saved.
    """

    crawler_class = CRAWLERS.get(chain)
    if not crawler_class:
        raise ValueError(f"Unknown retail chain: {chain}")

    crawler = crawler_class()
    try:
        stores = crawler.get_all_products(date)
    except Exception as err:
        logger.error(
            f"Error crawling {chain} for {date:%Y-%m-%d}: {err}", exc_info=True
        )
        return

    if not stores:
        logger.error(f"No stores imported for {chain} on {date}")
        return

    save_chain(path, stores)


def crawl(
    root: Path,
    date: datetime.date | None = None,
    chains: list[str] | None = None,
) -> Path:
    """
    Crawl multiple retail chains for product/pricing data and save it.

    Args:
        root: The base directory path where the data will be saved.
        date: The date for which to fetch the product data. If None, uses today's date.
        chains: List of retail chain names to crawl. If None, crawls all available chains.

    Returns:
        Path to the created ZIP archive file.
    """

    if chains is None:
        chains = get_chains()

    if date is None:
        date = datetime.date.today()

    path = root / date.strftime("%Y-%m-%d")
    zip_path = root / f"{date:%Y-%m-%d}.zip"
    os.makedirs(path, exist_ok=True)

    t0 = time()
    for chain in chains:
        logger.info(f"Starting crawl for {chain} on {date:%Y-%m-%d}")
        crawl_chain(chain, date, path / chain)
    t1 = time()

    logger.info(f"Crawled {','.join(chains)} for {date:%Y-%m-%d} in {t1 - t0:.2f}s")

    copy_archive_info(path)
    create_archive(path, zip_path)

    logger.info(f"Created archive {zip_path} with data for {date:%Y-%m-%d}")
    return zip_path
