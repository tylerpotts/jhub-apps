# TODO: Fix this hardcoding
import string
import typing
from dataclasses import dataclass

from jhub_apps.spawner.types import Framework

DEFAULT_CMD = ["python", "-m", "jhsingle_native_proxy.main", "--authtype=none"]

EXAMPLES_FILE = {
    Framework.panel.value: "panel_basic.py",
    Framework.bokeh.value: "bokeh_basic.py",
    Framework.streamlit.value: "streamlit_app.py",
    Framework.plotlydash.value: "plotlydash_app.py",
    Framework.voila.value: "voila_basic.ipynb",
    Framework.gradio.value: "gradio_basic.py",
}


@dataclass
class TString:
    value: str

    def replace(self, **kwargs):
        template = string.Template(self.value)
        keys_to_substitute = set()
        for k, v in kwargs.items():
            if f"${k}" in self.value:
                keys_to_substitute.add(k)
        subs = {k: v for k, v in kwargs.items() if k in keys_to_substitute}
        return template.substitute(subs)


@dataclass
class Command:
    args: typing.List[str]

    def get_substituted_args(self, **kwargs):
        subs_args = []
        for arg in self.args:
            s_arg = arg
            if isinstance(arg, TString):
                s_arg = arg.replace(**kwargs)
            subs_args.append(s_arg)
        return subs_args


COMMANDS = {
    Framework.gradio.value: Command(
        args=[
            "--destport=0",
            "python",
            TString("$filepath"),
            "{--}server-port={port}",
            TString("{--}root-path=$jh_service_prefix"),
            "--ready-check-path=/",
        ],
    ),
    Framework.voila.value: Command(
        args=[
            "--destport=0",
            "python",
            "{-}m",
            "voila",
            TString("$filepath"),
            "{--}port={port}",
            "{--}no-browser",
            "{--}Voila.server_url=/",
            "{--}Voila.ip=0.0.0.0",
            "{--}Voila.tornado_settings",
            "--debug",
            TString("allow_origin=$origin_host"),
            TString("{--}Voila.base_url=$voila_base_url"),
            "--progressive",
            "--ready-check-path=/voila/static/",
        ],
    ),
    Framework.streamlit.value: Command(
        args=[
            "--destport=0",
            "streamlit",
            "run",
            TString("$filepath"),
            "{--}server.port={port}",
            "{--}server.headless=True",
            TString("{--}browser.serverAddress=$origin_host"),
            "{--}browser.gatherUsageStats=false",
        ],
    ),
    Framework.plotlydash.value: Command(
        args=[
            "--destport=0",
            "python",
            "{-}m",
            "plotlydash_tornado_cmd.main",
            TString("$filepath"),
            "{--}port={port}",
        ],
    ),
    Framework.bokeh.value: Command(
        args=[
            "--destport=0",
            "python",
            "{-}m",
            "bokeh_root_cmd.main",
            TString("$filepath"),
            "{--}port={port}",
            TString("{--}allow-websocket-origin=$origin_host"),
            TString("{--}prefix=$base_url"),
            "--ready-check-path=/ready-check",
        ]
    ),
    Framework.panel.value: Command(
        args=[
            "--destport=0",
            "python",
            "{-}m",
            "bokeh_root_cmd.main",
            TString("$filepath"),
            "{--}port={port}",
            "{--}debug",
            TString("{--}allow-websocket-origin=$origin_host"),
            "{--}server=panel",
            TString("{--}prefix=$base_url"),
            "--ready-check-path=/ready-check",
        ]
    ),
}
