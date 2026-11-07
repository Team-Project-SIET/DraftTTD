class D5CensusInfo extends GSInfo {
    function GetAuthor() { return "Team-Project-SIET"; }
    function GetName() { return "D5CensusProof"; }
    function GetDescription() { return "One authorized read-only corridor box census"; }
    function GetVersion() { return 1; }
    function GetDate() { return "2026-11-02"; }
    function CreateInstance() { return "D5CensusProof"; }
    function GetShortName() { return "DCP1"; }
    function GetAPIVersion() { return "15"; }
}
RegisterGS(D5CensusInfo());
