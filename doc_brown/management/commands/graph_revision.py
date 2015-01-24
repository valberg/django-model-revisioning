# coding: utf-8
from django.core.management import BaseCommand, CommandError
from django.apps import apps


class Command(BaseCommand):

    args = '<model_path:label> <pk> <output>'
    help = 'Draw a graph over revisions for a given instance'

    def handle(self, *args, **options):
        try:
            import networkx as nx
        except ImportError:
            raise CommandError('networkx not installed.')

        try:
            from graphviz import Digraph
        except ImportError:
            raise CommandError('graphviz not installed.')

        model_path, pk, output = args
        app_name, model_name = model_path.split('.')
        model_name = model_name.split(':')
        if len(model_name) == 2:
            label = model_name[1]
        else:
            label = 'pk'
        model_name = model_name[0]

        app_config = apps.get_app_config(app_name)
        model = app_config.get_model(model_name)
        instance = model.objects.get(pk=pk)

        graph = Digraph()

        for revision in instance.revisions.all():
            graph.node(revision.pk, getattr(revision, label))

            if revision.parent_revision:
                graph.edge(revision.parent_revision.pk, revision.pk)

        graph.format = 'png'
        graph.render(filename='{}.gv'.format(output))
