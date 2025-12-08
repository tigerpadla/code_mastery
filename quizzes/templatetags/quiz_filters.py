"""
Custom template filters for quiz display.
"""

import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.filter(name='render_code')
def render_code(text):
    """
    Convert code tags to styled <code> elements.

    Handles:
    - [code]...[/code] tags for inline code
    - [codeblock]...[/codeblock] tags for multi-line code

    Usage: {{ question.text|render_code }}
    """
    if not text:
        return text

    # First escape HTML to prevent XSS
    text = escape(text)

    # Handle [codeblock]...[/codeblock] tags for multi-line code
    text = re.sub(
        r'\[codeblock\](.*?)\[/codeblock\]',
        r'<pre><code class="code-block">\1</code></pre>',
        text,
        flags=re.DOTALL
    )

    # Handle [code]...[/code] tags for inline code
    text = re.sub(
        r'\[code\](.*?)\[/code\]',
        r'<code class="code-inline">\1</code>',
        text,
        flags=re.DOTALL
    )

    return mark_safe(text)
