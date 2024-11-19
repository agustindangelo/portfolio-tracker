# Portfolio Tracker
Pass arguments in the form: <verb> <symbol> <quantity> <price>
Examples:
```
python . add 10 GGAL 12.5 ARS
python . sub 10 GGAL 12.5 ARS
```
Or even better, use a
## Powershell Alias
```powershell
function Invoke-PortfolioTracker {
    param (
        [string[]]$scriptArgs = @("report"),
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$extraArgs
    )
    $scriptPath = "C:\Users\adangelo\code\portfolio-tracker\portfolio-tracker"
    $currentLocation = Get-Location

    Set-Location $scriptPath

    # Combine scriptArgs and extraArgs into a single array
    $argsArray = @($scriptArgs + $extraArgs)

    # Call Python with arguments as an array
    python . @argsArray

    Set-Location -Path $currentLocation
}
Set-Alias pt Invoke-PortfolioTracker
```

Examples:
```
pt report
pt add 10 GGAL 12.5 USD
```