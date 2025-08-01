"""Chain that runs an arbitrary python function."""

import functools
import logging
from collections.abc import Awaitable
from typing import Any, Callable, Optional

from langchain_core.callbacks import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from pydantic import Field
from typing_extensions import override

from langchain.chains.base import Chain

logger = logging.getLogger(__name__)


class TransformChain(Chain):
    """Chain that transforms the chain output.

    Example:
        .. code-block:: python

            from langchain.chains import TransformChain
            transform_chain = TransformChain(input_variables=["text"],
             output_variables["entities"], transform=func())

    """

    input_variables: list[str]
    """The keys expected by the transform's input dictionary."""
    output_variables: list[str]
    """The keys returned by the transform's output dictionary."""
    transform_cb: Callable[[dict[str, str]], dict[str, str]] = Field(alias="transform")
    """The transform function."""
    atransform_cb: Optional[Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]] = (
        Field(None, alias="atransform")
    )
    """The async coroutine transform function."""

    @staticmethod
    @functools.lru_cache
    def _log_once(msg: str) -> None:
        """Log a message once.

        :meta private:
        """
        logger.warning(msg)

    @property
    def input_keys(self) -> list[str]:
        """Expect input keys.

        :meta private:
        """
        return self.input_variables

    @property
    def output_keys(self) -> list[str]:
        """Return output keys.

        :meta private:
        """
        return self.output_variables

    @override
    def _call(
        self,
        inputs: dict[str, str],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> dict[str, str]:
        return self.transform_cb(inputs)

    @override
    async def _acall(
        self,
        inputs: dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> dict[str, Any]:
        if self.atransform_cb is not None:
            return await self.atransform_cb(inputs)
        self._log_once(
            "TransformChain's atransform is not provided, falling"
            " back to synchronous transform",
        )
        return self.transform_cb(inputs)
