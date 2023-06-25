from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    network,
    Box,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    BoxV2,
    config,
)


def main():
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    box = Box.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )

    proxy_admin = ProxyAdmin.deploy({"from": account})

    box_encoded_initializer_function = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to V2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)

    # upgrade
    box_v2 = BoxV2.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    print("Proxy has been upgraded!")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    transaction_inc = proxy_box.increment({"from": account})
    transaction_inc.wait(1)
    print(proxy_box.retrieve())
