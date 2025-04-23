{
// selects hierarchy //
select -hi;

// select only the joints in the hierarchy //   
$sel = `ls -sl -typ "joint"`; 
select -r $sel;

// run once for each joint //
for($obj in $sel)
    {
    // check if attribute exists, coded this way for readability
    $exists = `attributeExists "lockInfluenceWeights" $obj`;

    if($exists == 1)
        {
            // delete attribute
            deleteAttr -at "lockInfluenceWeights" $obj;
        }
    }
}