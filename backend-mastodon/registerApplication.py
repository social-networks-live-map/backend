from mastodon import Mastodon

Mastodon.create_app(
    'social-networks-live-map',
    api_base_url = 'https://mastodon.social',
    to_file = 'backend_mastodon_clientcred.secret'
)
