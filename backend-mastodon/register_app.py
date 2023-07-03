from mastodon import Mastodon

Mastodon.create_app(
    'social-networks-live-map',
    api_base_url = 'https://mastodon.social',
    to_file = 'pytooter_clientcred.secret'
)
