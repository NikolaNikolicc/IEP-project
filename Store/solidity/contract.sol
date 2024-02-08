pragma solidity ^0.8.2;

contract myContract{
    address payable courier;
    address payable customer;
    address payable owner;

    bool paid = false;
    bool pickedUp = false;
    bool finished = false;
    uint price;

    modifier invalidCustomerCheck(){
        require(msg.sender == customer, "Invalid customer account.");
        _;
    }

    modifier transferNotCompleteCheck(){
        require(paid, "Transfer not complete.");
        _;
    }

    modifier deliveryNotCompleteCheck(){
        require(pickedUp, "Delivery not complete.");
        _;
    }

    modifier finishedCheck(){
        require(!finished, "This transaction has been finished.");
        _;
    }

    modifier insufficientFundsCheck(){
        require(msg.sender.balance >= price, "Insufficient funds.");
        _;
    }

    modifier transferAlreadyCompleteCheck(){
        require(!paid, "Transfer already complete.");
        _;
    }

    constructor(address payable c, uint p){
        customer = c;
        price = p;
    }

//    invalid customer check - msg.sender == customer, transfer not complete check - paid == true, delivery not complete check - pickedUp == true
    function delivery() external invalidCustomerCheck transferNotCompleteCheck deliveryNotCompleteCheck finishedCheck{
        owner.transfer(address(this).balance * 20 / 100);
        courier.transfer(address(this).balance - (address(this).balance * 20 / 100));
        finished = true;
    }

    function pick_up_order(address payable c) external transferNotCompleteCheck finishedCheck{
        courier = c;
        pickedUp = true;
    }

//    insufficient funds - msg.sender.balance >= price, transfer already complete - !paid
//    finishedCheck bespotreban - svakako ce biti nemoguce opet izvrsiti uplatu zbog transferAlreadyCompleteCheck
    function pay() external payable insufficientFundsCheck transferAlreadyCompleteCheck{
        paid = true;
    }

}