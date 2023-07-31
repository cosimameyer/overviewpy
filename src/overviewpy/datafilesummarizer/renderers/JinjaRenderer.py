import jinja2
import os


class JinjaRenderer:

    @staticmethod
    def render(context: dict) -> str:
        """
        Render the content of the context dictionary using the Jinja HTML template.

        :param context:
            A dictionary of data elements to pass to the Jinja template to render.
        :return:
            A string representing the rendered template.
        """
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(__file__), 'templates')
            )
        )

        render_template = environment.get_template('html-table.html.jinja')

        return render_template.render(context)
