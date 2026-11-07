class D5CargoFlowInfo extends GSInfo {
    function GetAuthor() { return "Team-Project-SIET"; }
    function GetName() { return "D5CargoFlowProof"; }
    function GetDescription() {
        return "One authorized read-only cargo-dispatch probe (protocol 10)";
    }
    function GetVersion() { return 1; }
    function GetDate() { return "2026-11-04"; }
    function CreateInstance() { return "D5CargoFlowProof"; }
    function GetShortName() { return "DCF1"; }
    function GetAPIVersion() { return "15"; }
}
RegisterGS(D5CargoFlowInfo());
