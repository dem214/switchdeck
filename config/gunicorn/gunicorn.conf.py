import multiprocessing

wsgi_app = 'switchdeck.wsgi'
bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
forwerded_allow_ips = 'nginx'