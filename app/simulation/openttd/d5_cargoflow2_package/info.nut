class D5CargoFlow2Info extends GSInfo {
    function GetAuthor() { return "Team-Project-SIET"; }
    function GetName() { return "D5CargoFlow2Proof"; }
    function GetDescription() {
        return "One authorized road-vehicle cargo-flow delivery attempt (protocol 11)";
    }
    function GetVersion() { return 1; }
    function GetDate() { return "2026-11-04"; }
    function CreateInstance() { return "D5CargoFlow2Proof"; }
    function GetShortName() { return "DCF2"; }
    function GetAPIVersion() { return "15"; }
}
RegisterGS(D5CargoFlow2Info());
