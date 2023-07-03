from mastodon import Mastodon

mastodon = Mastodon(client_id = 'pytooter_clientcred.secret',)
mastodon.log_in(
    'your@email',
    'password',
    to_file = 'pytooter_usercred.secret'
)
