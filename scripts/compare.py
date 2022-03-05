from brownie import (Contract, accounts, ERC20Mock, interface, Plain4Basic, MetaUSD)
from brownie.network.state import TxHistory

history = TxHistory()

susd_address = "0x57ab1ec28d129707052df4df418d58a2d46d5f51"
usdc_address = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
usdt_address = "0xdac17f958d2ee523a2206206994597c13d831ec7"
dai_address = "0x6b175474e89094c44da98b954eedeac495271d0f"
old_susd_pool_address = "0xA5407eAE9Ba41422680e2e00537571bcC53efBfD"
threepool_address = "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7"

old_pool = Contract.from_explorer(old_susd_pool_address)

def get_ERC20(address):
    return interface.IERC20(address)

def get_rate_multipler(ERC20):
    return 10**(36-ERC20.decimals())

def main():
    token_address_list = [dai_address, usdc_address, usdt_address, susd_address]
    token_list = map(get_ERC20, token_address_list)
    old_pool_balance = []
    three_pool_balance = []
    for token in token_list:
        ERC20Mock.deploy("mock {}".format(token.name()), token.symbol(), token.decimals(), {'from': accounts[0]})
        old_pool_balance.append(token.balanceOf(old_susd_pool_address))
        three_pool_balance.append(token.balanceOf(threepool_address))
    for i in range(4):
        ERC20Mock[i]._mint_for_testing(accounts[0], old_pool_balance[i], {'from': accounts[0]})
        ERC20Mock[i]._mint_for_testing(accounts[1], three_pool_balance[i], {'from': accounts[1]})
    rate_mutipler = map(get_rate_multipler, [ERC20Mock[0], ERC20Mock[1], ERC20Mock[2]])
    Plain4Basic.deploy({'from': accounts[0]})
    tx = Plain4Basic[0].initialize("3pool", "3pool", [ERC20Mock[0].address, ERC20Mock[1].address, ERC20Mock[2].address], list(rate_mutipler), 2000, 40000, {'from': accounts[0]})
    for i in range(3):
        ERC20Mock[i].approve(Plain4Basic[0].address, 2**254, {'from': accounts[0]})
        ERC20Mock[i].approve(Plain4Basic[0].address, 2**254, {'from': accounts[1]})
    Plain4Basic[0].add_liquidity(three_pool_balance[:3], 0, {'from': accounts[1]})
    Plain4Basic[0].add_liquidity(old_pool_balance[:3], 0, {'from': accounts[0]})
    MetaUSD.deploy({'from': accounts[0]})
    MetaUSD[0].initialize("sUSD", "sUSD", [ERC20Mock[3].address, Plain4Basic[0].address], get_rate_multipler(ERC20Mock[3]), 100, 4000000, Plain4Basic[0].address, [ERC20Mock[0].address, ERC20Mock[1].address, ERC20Mock[2].address], {'from': accounts[0]})
    Plain4Basic[0].approve(MetaUSD[0].address, 2**254, {'from': accounts[0]})
    ERC20Mock[3].approve(MetaUSD[0], 2**254, {'from': accounts[0]})
    MetaUSD[0].add_liquidity([old_pool_balance[3], Plain4Basic[0].balanceOf(accounts[0])], 0, {'from': accounts[0]})
    print("sUSD => DAI")
    for i in [10**x for x in range(3,8)]:
        for j in [1,2,5]:
            balance = i*j
            adjusted_balance = balance*10**18
            decimals = 10**ERC20Mock[0].decimals()
            old = old_pool.get_dy(3,0, adjusted_balance)
            new = MetaUSD[0].get_dy_underlying(0, 1, adjusted_balance)
            print("{}, {:.6f}, {:.6f}, {:.3f}".format(balance, old/decimals, new/decimals, new/old))
    print("sUSD => USDC")
    for i in [10**x for x in range(3,8)]:
        for j in [1,2,5]:
            balance = i*j
            adjusted_balance = balance*10**18
            decimals = 10**ERC20Mock[0].decimals()
            old = old_pool.get_dy(3,0, adjusted_balance)
            new = MetaUSD[0].get_dy_underlying(0, 1, adjusted_balance)
            print("{}, {:.6f}, {:.6f}, {:.3f}".format(balance, old/decimals, new/decimals, new/old))
    print("sUSD => USDT")
    for i in [10**x for x in range(3,8)]:
        for j in [1,2,5]:
            balance = i*j
            adjusted_balance = balance*10**18
            decimals = 10**ERC20Mock[0].decimals()
            old = old_pool.get_dy(3,0, adjusted_balance)
            new = MetaUSD[0].get_dy_underlying(0, 1, adjusted_balance)
            print("{}, {:.6f}, {:.6f}, {:.3f}".format(balance, old/decimals, new/decimals, new/old))