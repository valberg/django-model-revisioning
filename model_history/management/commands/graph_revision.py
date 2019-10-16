# coding: utf-8
from django.apps import apps
from django.core.management import BaseCommand
from django.core.management import CommandError


class Command(BaseCommand):

    args = "<model_path:label> <pk> <output>"
    help = "Draw a graph over revisions for a given instance"

    def add_arguments(self, parser):
        parser.add_argument("model_path", type=str)
        parser.add_argument("pk", type=str)
        parser.add_argument("output", type=str)

    def handle(self, *args, **options):
        try:
            import networkx as nx  # noqa
        except ImportError:
            raise CommandError("networkx not installed.")

        try:
            from graphviz import Digraph
        except ImportError:
            raise CommandError("graphviz not installed.")

        model_path = options["model_path"]
        pk = options["pk"]
        output = options["output"]

        app_name, model_name = model_path.split(".")
        model_name = model_name.split(":")
        if len(model_name) == 2:
            label = model_name[1]
        else:
            label = "pk"
        model_name = model_name[0]

        app_config = apps.get_app_config(app_name)
        model = app_config.get_model(model_name)
        instance = model.objects.get(pk=pk)

        graph = Digraph()
        graph.attr("node", shape="box")

        for revision in instance.revisions.all():
            text = str(getattr(revision, label))
            if revision == instance.current_revision:
                text += " (HEAD)"
                graph.attr("node", fillcolor="green", style="filled")

            graph.node(str(revision.pk), label=text)

            graph.attr("node", fillcolor="white", style="filled")

            if revision.parent_revision:
                graph.edge(str(revision.parent_revision.pk), str(revision.pk))

        graph.format = "png"
        graph.render(filename="{}.gv".format(output))
