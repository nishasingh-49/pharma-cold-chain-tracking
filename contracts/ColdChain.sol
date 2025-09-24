pragma solidity ^0.8.0; 

contract ColdChain {
    struct TempLog {
        uint256 timestamp;
        int256 temp; 
        string location;
    }

    struct Shipment {
        string shipmentID;
        string status; 
        address custodian; 
        int256 maxTempLimit; 
        int256 minTempLimit; 
        TempLog[] tempHistory;
        string productDetails; 
    }

    mapping(string => Shipment) public shipments; 

    event ShipmentCreated(string indexed shipmentID, address indexed manufacturer, string productDetails);
    event TemperatureUpdated(string indexed shipmentID, int256 currentTemp, string location);
    event FaultDetected(string indexed shipmentID, int256 currentTemp, address indexed custodian);
    event CustodyTransferred(string indexed shipmentID, address indexed oldCustodian, address indexed newCustodian);


    modifier onlyManufacturer() {
        require(msg.sender == owner, "Only manufacturer can call this function");
        _;
    }
    
    modifier onlyOracle() {
        require(msg.sender == iotOracle, "Only IoT Oracle can call this function");
        _;
    }

    address public owner; 
    address public iotOracle; 

    constructor(address _iotOracleAddress) {
        owner = msg.sender;
        iotOracle = _iotOracleAddress;
    }

    function createShipment(string memory _shipmentID, string memory _productDetails) public onlyManufacturer returns (bool) {
        require(bytes(shipments[_shipmentID].shipmentID).length == 0, "Shipment with this ID already exists");

        shipments[_shipmentID] = Shipment({
            shipmentID: _shipmentID,
            status: "Created",
            custodian: msg.sender,
            maxTempLimit: 8, 
            minTempLimit: 2, 
            tempHistory: new TempLog[](0), 
            productDetails: _productDetails
        });

        emit ShipmentCreated(_shipmentID, msg.sender, _productDetails);
        return true;
    }

    function updateTemperature(string memory _shipmentID, int256 _currentTemp, string memory _location) public onlyOracle returns (bool) {
        Shipment storage targetShipment = shipments[_shipmentID];
        require(bytes(targetShipment.shipmentID).length > 0, "Shipment does not exist");
        
        targetShipment.tempHistory.push(TempLog({
            timestamp: block.timestamp,
            temp: _currentTemp,
            location: _location
        }));
        
        emit TemperatureUpdated(_shipmentID, _currentTemp, _location);

        if (_currentTemp > targetShipment.maxTempLimit || _currentTemp < targetShipment.minTempLimit) {
            if (keccak256(abi.encodePacked(targetShipment.status)) != keccak256(abi.encodePacked("Compromised"))) {
                targetShipment.status = "Compromised";
                emit FaultDetected(_shipmentID, _currentTemp, targetShipment.custodian);
            }
        }

        // SAVE(targetShipment); 
        return true;
    }

    function transferCustody(string memory _shipmentID, address _newCustodian) public returns (bool) {
        Shipment storage targetShipment = shipments[_shipmentID];
        require(bytes(targetShipment.shipmentID).length > 0, "Shipment does not exist");
        require(msg.sender == targetShipment.custodian, "Only current custodian can transfer custody");
        require(keccak256(abi.encodePacked(targetShipment.status)) != keccak256(abi.encodePacked("Compromised")), "Shipment is compromised and cannot be transferred");
        
        address oldCustodian = targetShipment.custodian;
        targetShipment.custodian = _newCustodian;
        targetShipment.status = "In-Transit"; 
        
        emit CustodyTransferred(_shipmentID, oldCustodian, _newCustodian);

        // SAVE(targetShipment); 
        return true;
    }

    function getShipmentStatus(string memory _shipmentID) public view returns (string memory) {
        return shipments[_shipmentID].status;
    }

    function getShipmentCustodian(string memory _shipmentID) public view returns (address) {
        return shipments[_shipmentID].custodian;
    }

    function getShipmentDetails(string memory _shipmentID) public view returns (string memory id, string memory status, address custodian, int256 minTempLimit, int256 maxTempLimit) {
        Shipment storage s = shipments[_shipmentID];
        require(bytes(s.shipmentID).length > 0, "Shipment does not exist"); 
        return (s.shipmentID, s.status, s.custodian, s.minTempLimit, s.maxTempLimit);
    }

    function getShipmentProductDetails(string memory _shipmentID) public view returns (string memory) {
        Shipment storage s = shipments[_shipmentID];
        require(bytes(s.shipmentID).length > 0, "Shipment does not exist");
        return s.productDetails;
    }

    function getTempHistoryCount(string memory _shipmentID) public view returns (uint256) {
        Shipment storage s = shipments[_shipmentID];
        require(bytes(s.shipmentID).length > 0, "Shipment does not exist");
        return s.tempHistory.length;
    }

    function getTempHistoryEntry(string memory _shipmentID, uint256 _index) public view returns (uint256 timestamp, int256 temp, string memory location) {
        Shipment storage s = shipments[_shipmentID];
        require(bytes(s.shipmentID).length > 0, "Shipment does not exist");
        require(_index < s.tempHistory.length, "Index out of bounds");
        TempLog storage log = s.tempHistory[_index];
        return (log.timestamp, log.temp, log.location);
    }
}