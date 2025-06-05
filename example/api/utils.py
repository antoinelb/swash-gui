from typing import Any, Awaitable, Callable

from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response


async def get_query_string_params(
    req: Request,
    args: list[str] | None = None,
    opt_args: list[str] | None = None,
) -> dict[str, Any] | Response:
    if args is None:
        args = []
    if opt_args is None:
        opt_args = []
    try:
        args_ = {arg: req.query_params[arg] for arg in args}
        opt_args_ = {
            arg: req.query_params[arg]
            for arg in opt_args
            if arg in req.query_params
        }
    except KeyError:
        return PlainTextResponse(
            "There are missing parameters.", status_code=400
        )
    return {**args_, **opt_args_}


def with_query_string_params(
    args: list[str] | str | None = None,
    opt_args: list[str] | str | None = None,
) -> Callable[[Callable], Callable]:
    def decorator(
        fct: Callable[..., Awaitable[Response]],
    ) -> Callable[..., Awaitable[Response]]:
        async def wrapper(
            req: Request, *args_: Any, **kwargs_: Any
        ) -> Response:
            params = await get_query_string_params(
                req,
                args=[args] if isinstance(args, str) else args,
                opt_args=[opt_args] if isinstance(opt_args, str) else opt_args,
            )
            if isinstance(params, Response):
                return params
            params = {
                arg.replace("-", "_"): val for arg, val in params.items()
            }
            return await fct(req, *args_, **kwargs_, **params)

        return wrapper

    return decorator
