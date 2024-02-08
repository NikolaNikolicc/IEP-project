from web3 import Web3, HTTPProvider

web3 = Web3(HTTPProvider("http://ganache:8545"))

def readFile(path):
    with open(path, "r") as file:
        return file.read()


bytecode = readFile("./solidity/output/myContract.bin")
abi = readFile("./solidity/output/myContract.abi")

solidityContract = web3.eth.contract(bytecode = bytecode, abi = abi)
owner = web3.eth.accounts[0]