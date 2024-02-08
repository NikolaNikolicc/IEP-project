# TESTS DESCRIPTION
# python main.py --help

# TESTS WITHOUT BLOCKCHAIN

# python main.py --help
# python main.py --type "authentication" --authentication-url "http://127.0.0.1:5000" --jwt-secret "JWT_SECRET_KEY" --roles-field "roleId" --owner-role "owner" --customer-role "customer" --courier-role "courier"
# python main.py --type "level0" --with-authentication --authentication-url "http://127.0.0.1:5000" --owner-url "http://127.0.0.1:5001" --customer-url "http://127.0.0.1:5002"
# python main.py --type "level1" --with-authentication --authentication-url "http://127.0.0.1:5000" --owner-url "http://127.0.0.1:5001" --customer-url "http://127.0.0.1:5002"
# python main.py --type "level2" --with-authentication --authentication-url "http://127.0.0.1:5000" --owner-url "http://127.0.0.1:5001" --customer-url "http://127.0.0.1:5002" --courier-url "http://127.0.0.1:5003"
# python main.py --type "level3" --with-authentication --authentication-url "http://127.0.0.1:5000" --owner-url "http://127.0.0.1:5001" --customer-url "http://127.0.0.1:5002" --courier-url "http://127.0.0.1:5003"
# python main.py --type "all" --authentication-url "http://127.0.0.1:5000" --jwt-secret "JWT_SECRET_KEY" --roles-field "roleId" --owner-role "owner" --customer-role "customer" --courier-role "courier" --with-authentication --owner-url "http://127.0.0.1:5001" --customer-url "http://127.0.0.1:5002" --courier-url "http://127.0.0.1:5003"

# TESTS WITH BLOCKCHAIN

# python .\initialize_customer_account.py

# python main.py --type level1 --with-authentication --authentication-url http://127.0.0.1:5000 --owner-url http://127.0.0.1:5001 --customer-url http://127.0.0.1:5002 --with-blockchain --provider-url http://127.0.0.1:8545 --customer-keys-path ./keys.json --customer-passphrase iep_project --owner-private-key 0xd55a341e728f3ae7a68898aa5cef359e6129cdb06f9b11d847fe6e35fcbd722b
# python main.py --type level2 --with-authentication --authentication-url http://127.0.0.1:5000 --owner-url http://127.0.0.1:5001 --customer-url http://127.0.0.1:5002 --courier-url http://127.0.0.1:5003 --with-blockchain --provider-url http://127.0.0.1:8545 --customer-keys-path ./keys.json --customer-passphrase iep_project --owner-private-key 0x628a55044d0b5378cd121aa7db4bccbb89847901d1dc1ac4229df4f5370969c1 --courier-private-key 0x674421f95e661015e704dca97c762eabe891f9d0d0f64810e5415ad58c209701
# python main.py --type level3 --with-authentication --authentication-url http://127.0.0.1:5000 --owner-url http://127.0.0.1:5001 --customer-url http://127.0.0.1:5002 --courier-url http://127.0.0.1:5003 --with-blockchain --provider-url http://127.0.0.1:8545 --customer-keys-path ./keys.json --customer-passphrase iep_project --owner-private-key 0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60 --courier-private-key 0xbe07088da4ecd73ecb3d9d806cf391dfaef5f15f9ee131265da8af81728a4379
python main.py --type all --authentication-url http://127.0.0.1:5000 --jwt-secret JWT_SECRET_KEY --roles-field roles --owner-role owner --customer-role customer --courier-role courier --with-authentication --owner-url http://127.0.0.1:5001 --customer-url http://127.0.0.1:5002 --courier-url http://127.0.0.1:5003 --with-blockchain --provider-url http://127.0.0.1:8545 --customer-keys-path ./keys.json --customer-passphrase iep_project --owner-private-key 0x362942d376b866c425a0578205653e0e096b43b97190b9ff066660c16377ffc8 --courier-private-key 0x491cab6b42c76bf2f35eb01aea931fcd7cd9a470a2bfc00c8bd071a377eb9cb4