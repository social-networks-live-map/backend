from mastodon import Mastodon

mastodon = Mastodon(client_id = 'backend_mastodon_clientcred.secret',)
mastodon.log_in(
    'your@email',
    'password',
    to_file = 'backend_mastodon_usercred.secret'
)
