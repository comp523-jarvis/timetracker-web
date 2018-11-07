from django import template


register = template.Library()


@register.filter
def time_delta_as_hours(time_delta):
    seconds = time_delta.total_seconds()

    hours = int(seconds // (60 * 60))
    seconds -= hours * 60 * 60

    minutes = int(seconds // 60)

    return f'{hours}:{minutes:02}'
