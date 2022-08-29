import dataclasses
import os

import click
import mistune
import notion_client

import notionfier.plugins.footnotes


@click.group()
def cli():
    pass


@cli.command
@click.option("--token", type=str, required=True, help="The Notion auth token.")
@click.option("--parent_page_id", type=str, required=True, help="The page id of the parent page.")
@click.option("--file_path", type=str, required=True, help="Path to your markdown file.")
def import_notion(token: str, parent_page_id: str, file_path: str):
    with open(file_path, "r", encoding="utf-8") as fi:
        content = fi.read()

    md = mistune.create_markdown(
        renderer=notionfier.MyRenderer(),
        plugins=[
            mistune.plugins.plugin_task_lists,
            mistune.plugins.plugin_table,
            mistune.plugins.plugin_url,
            mistune.plugins.plugin_def_list,
            mistune.plugins.plugin_strikethrough,
            notionfier.plugins.plugin_footnotes,
        ],
    )
    result = md(content)

    params = {
        "parent": {"page_id": parent_page_id},
        "properties": {"title": {"title": [{"text": {"content": os.path.basename(file_path)}}]}},
        "children": [
            dataclasses.asdict(x, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
            for x in result
        ],
    }

    client = notion_client.Client(auth=token)
    client.pages.create(**params)


if __name__ == "__main__":
    cli()
