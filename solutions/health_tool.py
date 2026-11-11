"""One possible solution to the read-only health exercise."""


def health_summary(health):
    if health.get('service')!='checkout':
        raise ValueError('Only checkout is supported')
    if health.get('status') not in ('healthy','unhealthy') or type(health.get('http_status')) is not int:
        raise ValueError('Missing or invalid health fields')
    return f"checkout is {health['status']} (HTTP {health['http_status']})"
