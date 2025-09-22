# Discord boti

Duchovní nástupci [DecimBOTa](https://github.com/Skavenlord58/DecimBot2) a [BasedSchizoBOTa](https://github.com/Skavenlord58/BasedSchizoBOT),
tentokrát vyvíjeni jako komunitní projekt v monorepu.

- [Šimek](https://cs.wikipedia.org/wiki/Miloslav_%C5%A0imek) je nástupce BasedSchizoBOTa (Šimek -> Schizo) (pamatuje se dobře podle S)
- [Grossmann](https://cs.wikipedia.org/wiki/Ji%C5%99%C3%AD_Grossmann) je nástupce DecimBOTa
- [Krampol](https://cs.wikipedia.org/wiki/Ji%C5%99%C3%AD_Krampol) je nástupce [DecimAutomation](https://github.com/Skavenlord58/DecimAutomation)

## Zprovoznění a prostředí

Na správu balíčků a verzí pythonu oužíváme [uv](https://docs.astral.sh/uv/).

- [instalace uv](https://docs.astral.sh/uv/getting-started/installation/)
- Vlézt do složky bota
  - ```shell
    cd grossmann
    ```
  - ```shell
    cd šimek
    ```
  - ```shell
    cd krampol
    ```
- Nainstalování závislostí
  - ```shell
    uv sync --frozen
    ```
  to nainstaluje vše potřebné do `.venv` složky u daného bota

- Lokální spuštění
  - ```shell
    uv run main.py
    ```

- Zamykání prostředí
  - ```shell
    uv lock
    ```

## Nasazení

Momentálně žádný bot neběží v dockeru, ale na bare-metalu.

## Vývoj

### Přidávání balíčků

Viz [dokumentaci](https://docs.astral.sh/uv/concepts/projects/dependencies/#adding-dependencies).
