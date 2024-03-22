ontology = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix mf: <http://example.org/mf> .

<mf:NamedEntity> a xsd:string .
<mf:Property> a <mf:NamedEntity> .
<mf:SubjectProperty> a <mf:Property> .
<mf:PropertyAddress> a <mf:NamedEntity> .
<mf:PropertyStreetNumber> a <mf:NamedEntity> .
<mf:PropertyStreetName> a <mf:NamedEntity> .
<mf:PropertyCity> a <mf:NamedEntity> .
<mf:PropertyZip> a <mf:NamedEntity> .
<mf:PropertyName> a <mf:NamedEntity> .
<mf:PropertyUnits> a <mf:NamedEntity> .
<mf:PropertyAppraisedValue> a <mf:NamedEntity> .
<mf:PropertyOwner> a <mf:NamedEntity> .
<mf:PropertyAppraiser> a <mf:NamedEntity> .
<mf:PropertyAppraisalRemarks> a <mf:NamedEntity> .
<mf:PropertyAppraisalDate> a xsd:date .
<mf:PropertyAppraisalMonth> a xsd:string .
<mf:PropertyAppraisalDay> a xsd:int .
<mf:PropertyAppraisalYear> a xsd:int .
<mf:PropertyAppraisal> a <mf:document> .
<mf:PropertyInspectionDate> a xsd:date .
<mf:PropertyInspectionMonth> a xsd:string .
<mf:PropertyInspectionDay> a xsd:int .
<mf:PropertyInspectionYear> a xsd:int .
<mf:PropertyTaxInformation> a <mf:NamedEntity> .
<mf:PropertyLandArea> a <mf:NamedEntity> .
<mf:PropertyZoning> a <mf:NamedEntity> .
<mf:PropertyLandValue> a <mf:NamedEntity> .
<mf:PropertyTopography> a <mf:NamedEntity> .
<mf:PropertyDrainage> a <mf:NamedEntity> .
<mf:PropertyUtilities> a <mf:NamedEntity> .
<mf:PropertyFloodZoneIndicator> a <mf:NamedEntity> .
<mf:PropertyEasement> a <mf:NamedEntity> .
<mf:PropertyEncroachment> a <mf:NamedEntity> .
<mf:PropertyBuildingType> a <mf:NamedEntity> .
<mf:PropertyConstructionType> a <mf:NamedEntity> .
<mf:PropertyBuildingType> a <mf:NamedEntity> .
<mf:PropertyQuality> a <mf:NamedEntity> .
<mf:PropertyYearBuilt> a <mf:NamedEntity> .
<mf:PropertyArchitectureStyle> a <mf:NamedEntity> .
<mf:PropertyBuildingCondition> a <mf:NamedEntity> .
<mf:PropertyEffectiveAge> a <mf:NamedEntity> .
<mf:PropertyRemainingEconomicLife> a <mf:NamedEntity> .
<mf:PropertyFoundationType> a <mf:NamedEntity> .
<mf:PropertyRoofCover> a <mf:NamedEntity> .
<mf:PropertyBuildingFrame> a <mf:NamedEntity> .
<mf:PropertyElevators> a <mf:NamedEntity> .
<mf:PropertyServiceAccess> a <mf:NamedEntity> .
<mf:PropertyHeating> a <mf:NamedEntity> .
<mf:PropertyCooling> a <mf:NamedEntity> .
<mf:PropertyParkingType> a <mf:NamedEntity> .
<mf:PropertyOccupancy> a <mf:NamedEntity> .
<mf:PropertyLTV> a <mf:NamedEntity> .
<mf:PropertyDCR> a <mf:NamedEntity> .



<mf:Property> <hasName> <mf:PropertyName> ;
	    <hasAddress> <mf:PropertyAddress> ;
	    <hasUnits> <mf:PropertyUnits> ;
	    <hasOwner> <mf:PropertyOwner> ;	    
	    <hasAppraisal> <mf:PropretyAppraisal> .

<mf:PropertyAppraisal> <hasTitle> xsd:string ;
		     <hasDate> <mf:PropertyAppraisalDate> ;
		     <hasAppraiser> <mf:PropertyAppraiser> ;
		     <hasRemarks> <mf:PropertyAppraisalRemarks> ;
		     <hasAppraisedValue> <mf:PropertyAppraisedValue> .

<mf:PropertyAddress> <hasStreetNumber> <mf:PropertyStreetNumber> ;
		      <hasStreetName> <mf:PropertyStreetName> ;
		       <hasCity> <mf:PropertyCity> ;
		      <hasState> <mf:PropertyState> ;
		      <hasZip> <mf:PropertyZip> .

<mf:PropertyAppraisalDate> <hasMonth> <mf:PropertyAppraisalMonth> ;
			   <hasDay> <mf:PropertyAppraisalDay> ;
			   <hasYear> <mf:PropertyAppraisalYear> .

<mf:PropertyInspectionDate> <hasMonth> <mf:PropertyInspectionMonth> ;
			   <hasDay> <mf:PropertyInspectionDay> ;
			   <hasYear> <mf:PropertyInspectionYear> .

<mf:PropertyOwner> rdfs:label "Owner" .
<mf:PropertyAppraisalDate> rdfs:label "Date of Report" , "Date of the appraisal" , "Date:".
<mf:PropertyInspectionDate> rdfs:label "Date of Inspection" , "Inspection Date".
<mf:PropertyAppraisedValue> rdfs:label "Assessed Value" , "Market Value" , "Final Value".
<mf:PropertyUnits> rdfs:label "Number of Units" .
<mf:PropertyTaxInformation> rdfs:label "Tax Identification:" .
<mf:PropertyLandArea> rdfs:label "Land Area:" .
<mf:PropertyZoning> rdfs:label "Zoning:" .
<mf:PropertyLandValue> rdfs:label "Land Value:" .
<mf:PropertyTopography> rdfs:label "Topography:" .
<mf:PropertyDrainage> rdfs:label "Drainage:" .
<mf:PropertyUtilities> rdfs:label "Utilities:" .
<mf:PropertyFloodZoneIndicator> rdfs:label "Flood Zone:" .
<mf:PropertyEasement> rdfs:label "Easements:" .
<mf:PropertyEncroachment> rdfs:label "Encroachments:" .
<mf:PropertyBuildingType> rdfs:label "Building Type:" .
<mf:PropertyConstructionType> rdfs:label "Construction:" .
<mf:PropertyBuildingType> rdfs:label "Number of Units" .
<mf:PropertyQuality> rdfs:label "Quality:" .
<mf:PropertyYearBuilt> rdfs:label "Year Built:" .
<mf:PropertyArchitectureStyle> rdfs:label "Architectural Style:" .
<mf:PropertyBuildingCondition> rdfs:label "Condition:" .
<mf:PropertyEffectiveAge> rdfs:label "Effective Age:" .
<mf:PropertyRemainingEconomicLife> rdfs:label "Remaining Economic Life:" .
<mf:PropertyFoundationType> rdfs:label "Foundation:" .
<mf:PropertyRoofCover> rdfs:label "Roof/Cover:" .
<mf:PropertyBuildingFrame> rdfs:label "Frame:" .
<mf:PropertyElevators> rdfs:label "Elevators:" .
<mf:PropertyServiceAccess> rdfs:label "Service / Access/ Overhead Doors:" .
<mf:PropertyHeating> rdfs:label "Heating:" .
<mf:SubjectProperty> rdfs:label "Subject Property" .
<mf:PropertyCooling> rdfs:label "Cooling:" .
<mf:PropertyParkingType> rdfs:label "Parking Type and Condition of Spaces:" .
<mf:PropertyLTV> rdfs:label "Loan to Value Ratio" .
<mf:PropertyDCR> rdfs:label "Debt Coverage Ratio" .
"""

def get_ontology():
    return ontology