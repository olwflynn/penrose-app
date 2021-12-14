// SPDX-License-Identifier: MIT
pragma solidity >=0.4.21 <0.7.0;

contract SimpleStorage {
  uint storedData;
  event StorageEvent(address user, uint amount);

  function set(uint x) public {
    storedData = x;
    emit StorageEvent(msg.sender, x);
  }

  function get() public view returns (uint) {
    return storedData;
  }
}
