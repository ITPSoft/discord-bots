# Format and lint all bots
foreach ($dir in 'grossmann', 'krampol', 'šimek') {
    cd $dir
    uv run ruff format
    uv run ruff check --fix
    cd ..
}
