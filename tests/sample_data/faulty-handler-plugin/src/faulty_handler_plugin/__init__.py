# SPDX-FileCopyrightText: 2024-present apetrynet <flehnerheener@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import TypeVar

PluginRegistry = TypeVar("PluginRegistry")


class MyFaultyHandler:
    def __init__(self):
        self.name = "myfaultyhandler"
        self.suffixes = []

    def write_to_string(self, s: str, some_arg: str) -> str:
        return f"I went through all this trouble and all I got was this value: {some_arg} " f"and this string: {s}"


# This module is missing a required "register_plugin" function and will fail on import


def my_reg_func(registrar: PluginRegistry):
    registrar.add_handler(MyFaultyHandler())
