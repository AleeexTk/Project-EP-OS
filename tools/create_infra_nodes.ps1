$root = 'C:\Users\Alex Bear\Desktop\EvoPyramid OS'

function New-NodeDir {
    param($path, $manifest)
    New-Item -ItemType Directory -Force -Path $path | Out-Null
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path "$path\.node_manifest.json" -Encoding UTF8
    Write-Host "[OK] $path"
}

# PHASE 1: orphan .py files -> create their node directories

# Z10 - CR Gateway (alpha SPINE, infra)
New-NodeDir "$root\alpha_Check_Z10" @{
    id='cr_gateway_z10'; title='CR Gateway'; z_level=10; sector='SPINE'
    coords=@{x=9;y=9;z=10}; layer_type='alpha'; kind='router'
    summary='Contract relay routes validated task envelopes from Alpha governance to Beta runtime.'
    state='active'; links=@('gen-pear','gen-async-jobs')
    runtime_canon_flag='canon'
}

New-Item -ItemType Directory -Force -Path "$root\alpha_Check_Z10" | Remove-Item -Force
