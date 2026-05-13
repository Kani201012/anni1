"""
QuantBengal Engine — scanner.py  v10.0  (Oracle VM Production Master)
======================================================================
PURPOSE:
  Morning market scan at 09:00 IST.
  Scans the Nifty 100 universe (top 50 by liquidity for speed).
  Finds institutional momentum setups — bullish and bearish.
  Sends results to Telegram and persists to Supabase market_scans table.

v10.0 UPGRADE over v9.0:
  [SCAN-9]  rank_indices_by_adx() — New public async method.
            Called by main.py's select_champion_index() to determine
            the "Champion" index for the trading session.
            Downloads 90 days of daily data for NIFTY, BANKNIFTY, and
            SENSEX, computes 14-period ADX on each, and returns a
            sorted dict: { "BANKNIFTY": 32.5, "NIFTY": 27.1, "SENSEX": 19.4 }
            in descending order (highest ADX first).
            This method is standalone — it does NOT interfere with the
            existing scan_market() method or Nifty-100 stock scan.
            All error handling is self-contained: failed downloads return
            score 0.0 for that index without raising an exception.

PRESERVED 100% FROM v9.0:
  - NIFTY_100 symbol list
  - All filter thresholds (BULL_ADX_MIN, BEAR_ADX_MIN, VOL_SPIKE, etc.)
  - scan_market() async wrapper
  - _run_scan_sync() synchronous engine
  - _analyse_symbol() per-symbol indicator logic
  - format_report() Telegram HTML formatter
  - All SCAN-1 through SCAN-8 changes
"""

import asyncio
import logging
from datetime import datetime

import pandas as pd
import yfinance as yf

from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator

logger = logging.getLogger("QB.Scanner")

# ── Nifty 100 — Top 50 by F&O liquidity (Yahoo Finance format) ───────────────
NIFTY_100 = [
    "RELIANCE.NS", "TCS.NS",        "HDFCBANK.NS",   "ICICIBANK.NS",  "BHARTIARTL.NS",
    "SBIN.NS",     "INFY.NS",       "LICI.NS",        "ITC.NS",        "HUL.NS",
    "LT.NS",       "BAJFINANCE.NS", "HCLTECH.NS",     "MARUTI.NS",     "SUNPHARMA.NS",
    "ADANIENT.NS", "KOTAKBANK.NS",  "TITAN.NS",       "ONGC.NS",       "TATAMOTORS.NS",
    "NTPC.NS",     "AXISBANK.NS",   "ADANIPORTS.NS",  "ASIANPAINT.NS", "COALINDIA.NS",
    "BAJAJFINSV.NS","ULTRACEMCO.NS","POWERGRID.NS",   "JSWSTEEL.NS",   "M&M.NS",
    "TATASTEEL.NS","SIEMENS.NS",    "HINDALCO.NS",    "GRASIM.NS",     "SBILIFE.NS",
    "BRITANNIA.NS","ADANIPOWER.NS", "CIPLA.NS",       "INDUSINDBK.NS", "DRREDDY.NS",
    "EICHERMOT.NS","WIPRO.NS",      "BPCL.NS",        "NESTLEIND.NS",  "BAJAJ-AUTO.NS",
    "TATACONSUM.NS","HAL.NS",       "DLF.NS",         "VBL.NS",        "BEL.NS",
]

# ── [SCAN-9] Index tickers for Champion scan ─────────────────────────────────
_INDEX_TICKERS = {
    "NIFTY":     "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX":    "^BSESN",
}

# ── Filter thresholds — UNCHANGED from v9.0 ───────────────────────────────────
BULL_ADX_MIN   = 25.0
BULL_RSI_MIN   = 55.0
BULL_VOL_SPIKE = 1.5
BEAR_ADX_MIN   = 25.0
BEAR_RSI_MAX   = 40.0
BEAR_VOL_SPIKE = 2.0
DATA_PERIOD    = "90d"
DATA_INTERVAL  = "1d"
TOP_N_RESULTS  = 5

# ADX indicator window shared across both scan types
_ADX_WINDOW    = 14
_ADX_MIN_ROWS  = _ADX_WINDOW * 2   # 28 rows needed for ADX warm-up


class MarketScanner:

    def __init__(self, symbols: list = None):
        self.symbols = symbols or NIFTY_100

    # ══════════════════════════════════════════════════════════════════════
    #  [SCAN-9] CHAMPION INDEX ADX RANKER
    # ══════════════════════════════════════════════════════════════════════

    async def rank_indices_by_adx(self) -> dict:
        """
        [SCAN-9] Computes 14-period ADX for NIFTY, BANKNIFTY, and SENSEX
        using 90 days of daily price data from yfinance.

        Returns:
            dict sorted by ADX descending, e.g.:
            {
                "BANKNIFTY": 34.2,
                "NIFTY":     28.7,
                "SENSEX":    21.1,
            }
            On complete failure, returns an empty dict — caller
            (select_champion_index in main.py) handles the fallback.

        Design decisions:
          - Uses "90d" period: sufficient for a warm 14-period ADX with
            plenty of buffer. 5d / 1d data is too shallow for reliable ADX.
          - Each index is downloaded individually (not bulk) because bulk
            yfinance download for index tickers (^NSEI, ^NSEBANK) is
            unreliable with MultiIndex column flattening.
          - Failure of any single index results in score 0.0 for that
            index, not a crash. The other indices are still ranked.
          - Runs in asyncio.to_thread() — never blocks the event loop.
        """
        logger.info("🏆 [SCAN-9] Index ADX ranking scan starting…")
        scores = await asyncio.to_thread(self._rank_indices_sync)
        if scores:
            sorted_scores = dict(
                sorted(scores.items(), key=lambda x: x[1], reverse=True)
            )
            logger.info(
                "🏆 [SCAN-9] Index ADX scores: "
                + " | ".join(f"{k}: {v:.1f}" for k, v in sorted_scores.items())
            )
            return sorted_scores
        logger.warning("🏆 [SCAN-9] Index ADX ranking returned no scores.")
        return {}

    def _rank_indices_sync(self) -> dict:
        """
        Synchronous inner function — runs in a thread pool via asyncio.to_thread().
        Downloads and scores each index independently so one failure cannot
        block the others.
        """
        scores = {}

        for name, ticker in _INDEX_TICKERS.items():
            try:
                raw = yf.download(
                    tickers  = ticker,
                    period   = DATA_PERIOD,     # "90d" — same as stock scan
                    interval = DATA_INTERVAL,   # "1d"
                    progress = False,
                )

                if raw is None or raw.empty:
                    logger.warning(
                        f"[SCAN-9] {name} ({ticker}): empty download — score 0."
                    )
                    scores[name] = 0.0
                    continue

                # ── Normalise columns ─────────────────────────────────────
                if isinstance(raw.columns, pd.MultiIndex):
                    raw.columns = [str(c[0]).lower() for c in raw.columns]
                else:
                    raw.columns = [str(c).lower() for c in raw.columns]

                raw.rename(
                    columns={"adj close": "close", "adj_close": "close"},
                    inplace=True,
                )

                # Ensure required OHLC columns exist
                for col in ("high", "low", "close"):
                    if col not in raw.columns:
                        logger.warning(
                            f"[SCAN-9] {name}: missing '{col}' column — score 0."
                        )
                        scores[name] = 0.0
                        break
                    raw[col] = pd.to_numeric(raw[col], errors="coerce").fillna(0.0)
                else:
                    # All required columns present — proceed
                    raw.dropna(subset=["close"], inplace=True)

                    if len(raw) < _ADX_MIN_ROWS:
                        logger.warning(
                            f"[SCAN-9] {name}: only {len(raw)} rows after "
                            f"cleaning (need ≥ {_ADX_MIN_ROWS}) — score 0."
                        )
                        scores[name] = 0.0
                        continue

                    adx_series = ADXIndicator(
                        high   = raw["high"].astype(float),
                        low    = raw["low"].astype(float),
                        close  = raw["close"].astype(float),
                        window = _ADX_WINDOW,
                    ).adx()

                    adx_value = float(adx_series.iloc[-1])

                    # Guard against NaN (can happen if series is too short)
                    if pd.isna(adx_value):
                        logger.warning(
                            f"[SCAN-9] {name}: ADX is NaN — score 0."
                        )
                        scores[name] = 0.0
                    else:
                        scores[name] = round(adx_value, 2)
                        logger.info(
                            f"[SCAN-9] {name} ({ticker}): "
                            f"ADX = {adx_value:.1f} | rows = {len(raw)}"
                        )

            except Exception as exc:
                # Individual index failure is non-fatal
                logger.warning(
                    f"[SCAN-9] {name} ({ticker}): download/compute failed "
                    f"— {exc}. Score set to 0."
                )
                scores[name] = 0.0

        return scores

    # ══════════════════════════════════════════════════════════════════════
    #  EXISTING SCAN METHODS — UNCHANGED from v9.0
    # ══════════════════════════════════════════════════════════════════════

    async def scan_market(self) -> tuple[list, list]:
        """
        [SCAN-7] Async entry point. Runs blocking stock scan in thread pool.

        Returns:
            (bullish_picks, bearish_picks) — plain lists of dicts,
            each containing: symbol, price, adx, rsi, vol_spike.
        """
        logger.info(
            f"🔍 Morning Market Scan starting | "
            f"{len(self.symbols)} symbols | "
            f"{datetime.now().strftime('%d-%b-%Y %H:%M IST')}"
        )
        return await asyncio.to_thread(self._run_scan_sync)

    def _run_scan_sync(self) -> tuple[list, list]:
        """
        Downloads data for all symbols, computes indicators,
        applies institutional filter criteria, and returns ranked picks.
        """
        bullish_picks = []
        bearish_picks = []

        logger.info(
            f"Downloading {len(self.symbols)} symbols | "
            f"period={DATA_PERIOD} interval={DATA_INTERVAL}"
        )
        try:
            raw_data = yf.download(
                self.symbols,
                period   = DATA_PERIOD,
                interval = DATA_INTERVAL,
                group_by = "ticker",
                progress = False,
                threads  = True,
            )
        except Exception as exc:
            logger.error(f"Bulk download failed: {exc}")
            return [], []

        for symbol in self.symbols:
            try:
                result = self._analyse_symbol(symbol, raw_data)
                if result is None:
                    continue
                if result["direction"] == "BULL":
                    bullish_picks.append(result["data"])
                elif result["direction"] == "BEAR":
                    bearish_picks.append(result["data"])
            except Exception as exc:
                logger.debug(f"Symbol {symbol} analysis failed: {exc}")
                continue

        bullish_picks = sorted(
            bullish_picks, key=lambda x: x["adx"], reverse=True
        )[:TOP_N_RESULTS]

        bearish_picks = sorted(
            bearish_picks, key=lambda x: x["adx"], reverse=True
        )[:TOP_N_RESULTS]

        logger.info(
            f"✅ Scan complete | "
            f"Bullish: {len(bullish_picks)} | Bearish: {len(bearish_picks)}"
        )
        return bullish_picks, bearish_picks

    def _analyse_symbol(self, symbol: str, raw_data) -> dict | None:
        """
        Computes indicators for a single symbol and applies filters.
        Returns {"direction": "BULL"|"BEAR", "data": {...}} or None.
        """
        try:
            if isinstance(raw_data.columns, pd.MultiIndex):
                df = raw_data[symbol].dropna()
            else:
                df = raw_data.dropna()
        except (KeyError, TypeError):
            return None

        if len(df) < 30:
            return None

        required = {"Close", "High", "Low", "Volume"}
        if not required.issubset(set(df.columns)):
            return None

        close = df["Close"].squeeze()
        high  = df["High"].squeeze()
        low   = df["Low"].squeeze()

        ema_9   = EMAIndicator(close=close, window=9).ema_indicator().iloc[-1]
        ema_21  = EMAIndicator(close=close, window=21).ema_indicator().iloc[-1]
        ema_200 = EMAIndicator(
            close=close, window=min(200, len(df) - 1)
        ).ema_indicator().iloc[-1]

        rsi = RSIIndicator(close=close, window=14).rsi().iloc[-1]

        adx = ADXIndicator(
            high=high, low=low, close=close, window=_ADX_WINDOW
        ).adx().iloc[-1]

        avg_vol   = df["Volume"].rolling(window=10).mean().iloc[-1]
        curr_vol  = df["Volume"].iloc[-1]
        vol_spike = float(curr_vol / avg_vol) if avg_vol > 0 else 0.0

        curr_price = float(close.iloc[-1])
        clean_sym  = symbol.replace(".NS", "")

        payload = {
            "symbol":    clean_sym,
            "price":     round(curr_price, 2),
            "adx":       round(float(adx),       1),
            "rsi":       round(float(rsi),        1),
            "vol_spike": round(vol_spike,          2),
            "ema_9":     round(float(ema_9),       2),
            "ema_21":    round(float(ema_21),      2),
            "ema_200":   round(float(ema_200),     2),
        }

        # [SCAN-2] Bullish filter
        is_bullish = (
            curr_price > ema_200
            and float(adx)       >= BULL_ADX_MIN
            and float(rsi)       >= BULL_RSI_MIN
            and vol_spike        >= BULL_VOL_SPIKE
            and ema_9            > ema_21
        )

        # [SCAN-2] Bearish filter
        is_bearish = (
            curr_price < ema_200
            and float(adx)  >= BEAR_ADX_MIN
            and float(rsi)  <= BEAR_RSI_MAX
            and vol_spike   >= BEAR_VOL_SPIKE
            and ema_9       < ema_21
        )

        if is_bullish:
            return {"direction": "BULL", "data": payload}
        if is_bearish:
            return {"direction": "BEAR", "data": payload}

        return None

    def format_report(self, bullish: list, bearish: list) -> str:
        """
        [SCAN-5] Formats scan results as HTML for Telegram.
        UNCHANGED from v9.0.
        """
        date_str = datetime.now().strftime("%d %b %Y")
        report   = (
            f"🐅 <b>QuantBengal Morning Scan</b>\n"
            f"📅 {date_str}\n"
            f"Filters: ADX≥25 | Vol≥1.5× | EMA Confluence\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        report += "🔥 <b>BULLISH SETUPS</b>\n"
        if not bullish:
            report += "• No high-conviction bullish setups today\n"
        else:
            for p in bullish:
                report += (
                    f"• <b>{p['symbol']}</b> ₹{p['price']:,.1f} "
                    f"| ADX:{p['adx']:.0f} RSI:{p['rsi']:.0f} "
                    f"Vol:{p['vol_spike']:.1f}×\n"
                )

        report += "\n❄️ <b>BEARISH SETUPS</b>\n"
        if not bearish:
            report += "• No high-conviction bearish setups today\n"
        else:
            for p in bearish:
                report += (
                    f"• <b>{p['symbol']}</b> ₹{p['price']:,.1f} "
                    f"| ADX:{p['adx']:.0f} RSI:{p['rsi']:.0f} "
                    f"Vol:{p['vol_spike']:.1f}×\n"
                )

        report += (
            "\n<i>These are informational setups only.\n"
            "All trades are executed by the automated engine.</i>"
        )
        return report
