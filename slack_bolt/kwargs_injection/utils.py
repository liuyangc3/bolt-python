# pytype: skip-file
import logging
from typing import Callable, Dict, Optional, Any, Sequence

from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse
from .args import Args
from slack_bolt.request.payload_utils import (
    to_options,
    to_shortcut,
    to_action,
    to_view,
    to_command,
    to_event,
    to_message,
    to_step,
)


def build_required_kwargs(
    *,
    logger: logging.Logger,
    required_arg_names: Sequence[str],
    request: BoltRequest,
    response: Optional[BoltResponse],
    next_func: Callable[[], None] = None,
) -> Dict[str, Any]:
    all_available_args = {
        "logger": logger,
        "client": request.context.client,
        "req": request,
        "request": request,
        "resp": response,
        "response": response,
        "context": request.context,
        # payload
        "body": request.body,
        "options": to_options(request.body),
        "shortcut": to_shortcut(request.body),
        "action": to_action(request.body),
        "view": to_view(request.body),
        "command": to_command(request.body),
        "event": to_event(request.body),
        "message": to_message(request.body),
        "step": to_step(request.body),
        # utilities
        "ack": request.context.ack,
        "say": request.context.say,
        "respond": request.context.respond,
        # middleware
        "next": next_func,
    }
    all_available_args["payload"] = (
        all_available_args["options"]
        or all_available_args["shortcut"]
        or all_available_args["action"]
        or all_available_args["view"]
        or all_available_args["command"]
        or all_available_args["event"]
        or all_available_args["message"]
        or all_available_args["step"]
        or request.body
    )
    for k, v in request.context.items():
        if k not in all_available_args:
            all_available_args[k] = v

    kwargs: Dict[str, Any] = {
        k: v for k, v in all_available_args.items() if k in required_arg_names
    }
    found_arg_names = kwargs.keys()
    for name in required_arg_names:
        if name == "args":
            if isinstance(request, BoltRequest):
                kwargs[name] = Args(**all_available_args)
            else:
                logger.warning(
                    f"Unknown Request object type detected ({type(request)})"
                )

        if name not in found_arg_names and name != 'self':
            logger.warning(f"{name} is not a valid argument")
            kwargs[name] = None
    return kwargs
