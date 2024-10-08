# SPDX-FileCopyrightText: 2024-present apetrynet <flehnerheener@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import TypeVar

PluginRegistry = TypeVar("PluginRegistry")


class MyHandler1:
    def __init__(self):
        self.name = "myhandler1"
        self.suffixes = []

    def write_to_string(self, s: str, some_arg: str) -> str:
        return f"I went through all this trouble and all I got was this value: {some_arg} " f"and this string: {s}"


class MyHandler2:
    def __init__(self):
        self.name = "myhandler2"
        self.suffixes = []

    def write_to_string(self, s: str, some_arg: str) -> str:
        return f"I went through all this trouble and all I got was this value: {some_arg} " f"and this string: {s}"


# This func is named in pyproject.toml
def register_plugin_func(registrar: PluginRegistry):
    registrar.add_handler(MyHandler1())


# This is the required function if no function is provided like above
def register_plugin(registrar: PluginRegistry):
    registrar.add_handler(MyHandler2())
