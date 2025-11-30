import asyncio
from typing import Dict, List

import numpy as np
import pandas as pd
from loguru import logger

from app.services.ohlcv_service import OHLCVService


class BacktestService:
    def __init__(self):
        self.ohlcv_service = OHLCVService()

    async def run_backtest(
        self,
        symbol: str,
        range_period: str = "1y",
        entry_threshold: float = 0.55,
        exit_threshold: float = 0.5,
        fee_bps: float = 10.0,
        slippage_bps: float = 5.0,
    ) -> Dict:
        """Run a simple long-only backtest based on a probability-like signal.

        The current implementation derives a heuristic "p_up" signal from
        price vs 20-day moving average so it can work without trained models.
        """
        logger.info(
            f"Running backtest for {symbol} period={range_period} "
            f"entry={entry_threshold} exit={exit_threshold} "
            f"fee_bps={fee_bps} slippage_bps={slippage_bps}"
        )

        data = await self.ohlcv_service.get_ohlcv(symbol, range_period)
        candles = data.get("candles", [])
        if not candles:
            raise ValueError(f"No OHLCV data available for {symbol}")

        df = pd.DataFrame(candles)
        df["time"] = pd.to_datetime(df["t"])
        df = df.set_index("time")
        df = df.rename(
            columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
        )
        df = df[["open", "high", "low", "close", "volume"]].dropna()

        if len(df) < 30:
            raise ValueError("Not enough data for backtest (need at least 30 bars)")

        # ------------------------------------------------------------------
        # Derive a simple probability-like signal p_up from price vs MA20.
        # p_up is scaled to [0, 1] where >0.5 is bullish, <0.5 bearish.
        # ------------------------------------------------------------------
        df["ma20"] = df["close"].rolling(window=20).mean()
        df["ma_ratio"] = df["close"] / df["ma20"]
        df["p_up"] = 0.5 + 0.5 * np.tanh((df["ma_ratio"] - 1.0) * 3.0)
        df = df.dropna()

        # Trading parameters
        fee = fee_bps / 10000.0
        slippage = slippage_bps / 10000.0

        equity = 1.0
        cash = equity
        position = 0.0
        entry_price = 0.0
        equity_curve: List[Dict] = []
        trade_pnls: List[float] = []

        close_prices = df["close"].to_numpy()
        p_up_values = df["p_up"].to_numpy()
        times = df.index.to_pydatetime()

        for i in range(1, len(df)):
            price = close_prices[i]
            signal = p_up_values[i]

            # Entry logic
            if position == 0.0 and signal > entry_threshold:
                # Buy 1 unit with fees & slippage
                buy_price = price * (1.0 + fee + slippage)
                if cash > 0:
                    position = cash / buy_price
                    cash = 0.0
                    entry_price = buy_price

            # Exit logic
            elif position > 0.0 and signal < exit_threshold:
                sell_price = price * (1.0 - fee - slippage)
                cash = position * sell_price
                trade_pnls.append((sell_price - entry_price) / entry_price)
                position = 0.0
                entry_price = 0.0

            # Mark-to-market equity
            equity = cash + position * price
            equity_curve.append({"t": times[i].isoformat(), "equity": float(equity)})

        # If still in position at the end, close it at last price
        if position > 0.0:
            final_price = close_prices[-1] * (1.0 - fee - slippage)
            final_cash = position * final_price
            trade_pnls.append((final_price - entry_price) / entry_price)
            equity = final_cash

        # Compute metrics
        eq_series = pd.Series([p["equity"] for p in equity_curve], index=[p["t"] for p in equity_curve])
        returns = eq_series.pct_change().dropna()

        sharpe = 0.0
        sortino = 0.0
        max_drawdown = 0.0

        if not returns.empty:
            mean_ret = returns.mean()
            std_ret = returns.std()
            neg_std = returns[returns < 0].std()

            if std_ret > 0:
                sharpe = float(mean_ret / std_ret * np.sqrt(252))
            if neg_std > 0:
                sortino = float(mean_ret / neg_std * np.sqrt(252))

            cum_max = eq_series.cummax()
            drawdown = (eq_series - cum_max) / cum_max
            max_drawdown = float(drawdown.min()) if not drawdown.empty else 0.0

        win_rate = 0.0
        if trade_pnls:
            wins = sum(1 for p in trade_pnls if p > 0)
            win_rate = float(wins / len(trade_pnls))

        result = {
            "symbol": symbol,
            "metrics": {
                "sharpe": sharpe,
                "sortino": sortino,
                "max_drawdown": max_drawdown,
                "win_rate": win_rate,
                "trades": len(trade_pnls),
                "start": times[0].isoformat(),
                "end": times[-1].isoformat(),
            },
            "equity_curve": equity_curve,
        }

        logger.info(
            f"Backtest complete for {symbol} | "
            f"Sharpe={sharpe:.2f} Sortino={sortino:.2f} "
            f"MDD={max_drawdown:.2%} WinRate={win_rate:.2%}"
        )

        return result
