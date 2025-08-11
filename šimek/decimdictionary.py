HELP = '''
    ***Bot commands:***
    _arguments in \{\} are optional, arguments with \[\] are required_
    $_bothelp_ or _commands_
        Shows help.
    $_ping_
        Shows bot's ping and API latency.
    $_roll_ \{number\}
        Rolls a random number between 1 and \{number\}. Defaults number to 100,
        if not specified.
    $_yesorno_
        Answers a question with yes or no.
    $_warcraft_ \{time\}
        Creates a warcraft play session announcement from template.
    $_gmod_ \{time\}
        Creates a gmod play session announcement from template.
    $_poll_ [name_of_poll] [option_1] [option2] \{option3\} \{option4\} \{option5\}
        Use underscores as spaces. Bot will automatically edit them for you.
    $_today_
        Tells you which international day it is today.
    '''

WARCRAFTY_CZ = '''
<@&871817685439234108> - Warcrafty 3 dnes{0}?
React with attendance:
:white_check_mark: Ano
:negative_squared_cross_mark: Ne
:thinking: Možná

Chceme hrát:
:one: - Survival Chaos
:two: - Legion TD nebo Element TD
:three: - Blood Tournament
:four: - Risk
:five: - Luckery/Uther Party/Temple Escape
:six: - Objevovat nové mapy.
:question: - Něco jiného? Napište jako reply.
'''

GMOD_CZ = '''
<@&951457356221394975> - Garry's Mod dnes{0}?
    React with attendance:
    :white_check_mark: Ano
    :negative_squared_cross_mark: Ne
    :thinking: Možná

    Chceme hrát:
    :one: - TTT (OG Among Us)
    :two: - PropHunt/Hide&Seek (schováváte se na mapě jako props a hlídači vás hledají)
    :three: - Stranded (RPG mapa, něco jako Rust)
    :four: - DropZone (arena s různýma spellama něco jako Warloci ve W3)
    :five: - Flood
    :question: - Něco jiného? Napište jako reply.

'''

MOT_HLASKY = [
    "Zatímco ztrácíme svůj čas váháním a odkládáním, život utíká.",
    "Přijmi to co je. Nech plavat to, co bylo. A měj víru v to, co přijde.",
    "Jestli chceš něco, co jsi nikdy neměl, tak musíš dělat něco, co jsi nikdy nedělal.",
    "Tvůj život je výsledkem rozhodnutí, které děláš. Pokud se ti tvůj život nelíbí, je čas vybrat si lépe.",
    "Lidé ve svém životě nelitují toho co udělali, ale toho co neudělali.",
    "Každá chyba je příležitostí se něčemu naučit. ",
    "Jedinou překážkou mezi tebou a tvým cílem je ten blábol, kterým si odůvodňuješ, proč to nejde.",
    "Přijít můžeš jen o to, co máš. To čím jsi, to neztratíš.",
    "Sebejistota nevychází z toho, že vždycky víš, co děláš, ale z toho, že se nebojíš šlápnout vedle.",
    "Víra znamená věřit tomu, co nevidíš. Za odměnu pak uvidíš to, v co věříš.",
    "Život není problém, který je třeba řešit, je to skutečnost, kterou je třeba poznat.",
    "Lva / Vlka nezajímá, co si o něm ovce myslí.",
    "Existuje tisíce způsobů, jak zabít čas, ale žádný, jak ho vzkřísit.",
    "Nemusíte být skvělí, abyste začali, ale musíte začít, abyste byli skvělí.",
    "Ničeho jsem nenabyl lehce, každá věc mně stála nejtvrdší práci. Nehledejte lehké cesty. Ty hledá tolik lidí, že se po nich nedá přijít nikam.",
    "Osud míchá karty, my hrajeme.",
    "Je jenom jedna cesta za štěstím a to přestat se trápit nad tím, co je mimo naši moc.",
    "Když něco opravdu chceš, celý vesmír se spojí, abys to mohl uskutečnit.",
    "Slaboši čekají na příležitost, silní ji vytvářejí.",
    "Představivost je důležitější než vědomosti.",
    "Vysoké cíle, třebaže nesplnitelné, jsou cennější než nízké, třebaže splnitelné.",
    "Co chceš, můžeš.",
    "Nejlepší způsob, jak se do něčeho pustit, je přestat o tom mluvit a začít to dělat.",
    "Nepřej si, aby to bylo snazší; přej si, abys byl lepší.",
    "Jestliže neumíš, naučíme, jestliže nemůžeš, pomůžeme ti, jestliže nechceš, nepotřebujeme tě.",
    "Čím jsem starší, tím méně si všímám, co lidé říkají, myslí si a v co doufají. Všímám si toho, co dělají, jak žijí a o co usilují.",
    "Žij, jako bys měl zítra zemřít. Uč se, jako bys měl navždy žít.",
    "Je lepší zemřít pro něco než žít pro nic.",
    "Život se nepíše, život se žije.",
    "Nauč se slzami v očích smát, nauč se pohladit se zavřenou dlaní, nauč se rozdat všechno a nemít nic, pak poznáš, že stojí za to žít.",
    "Pokud chcete být nenahraditelní, musíte být odlišní.",
    "Žijete jenom jednou. Tak by to měla být zábava.",
    "Svůj úspěch hodnoťte podle toho, čeho všeho jste se pro něj vzdali.",
    "Jestliže tvoje štěstí závisí na tom, co dělá někdo druhej, pak máš, myslím, problém!",
    "Jediná věc, která stojí mezi vámi a vaším cílem, jsou ty kecy o tom, jak to nezvládnete, které si neustále namlouváte.",
    "Člověk, který přichází s novou myšlenkou je blázen do té doby, než jeho myšlenka zvítězí.",
    "Není nic moudřejšího, než přesně vědět, kdy máš co začít a kdy s čím přestat.",
    "Jestli se ti něco nelíbí, změň to! Nejsi strom.",
    "Co tě nezabije, to tě posílí",
    "Svět je krásný a stojí za to o něj bojovat.",
    "Žádný člověk není takový hlupák, aby nedosáhl úspěchu aspoň v jedné věci, je-li vytrvalý.",
    "Nejde-li o život, jde o hovno.",
    "Stojí za to nebát se smrti, protože pak se neumíš bát ničeho.",
    "Včera jsem byl chytrý, proto jsem chtěl změnit svět. Dnes jsem moudrý, proto měním sám sebe.",
    "Můžete mít buď výmluvy nebo výsledky. Nikdy ne obojí.",
    "Šampióni nevznikají v posilovnách. Šampióni vznikají z něčeho, co mají hluboko v sobě – z touhy, snu a vize.",
    "Žij přítomností, sni o budoucnosti, uč se minulostí.",
    "Jediná omezení, která v lidských životech existují si klademe my sami.",
    "Není pravda, že máme málo času, avšak pravda je, že ho hodně promarníme.",
    "Dělej dobro a dobro se ti vrátí.",
    "Věřím, že fantazie je silnější než vědění. Že mýty mají větší moc než historie. Že sny jsou mocnější než skutečnost. Že naděje vždy zvítězí nad zkušeností. Že smích je jediným lékem na zármutek. A věřím, že láska je silnější než smrt.",
    "Neodpoutávej se nikdy od svých snů! Když zmizí, budeš dál existovat, ale přestaneš žít.",
    "Abyste mohl být ten nejlepší šampion, musíte věřit, že jím skutečně jste. Pokud nejste, musíte alespoň předstírat, že jím jste.",
    "Nejhorší ze všech tragédií není zemřít mladý, nýbrž žít do pětasedmdesáti, a přece nikdy nežít doopravdy.",
    "Nemůžeš-li létat, běž, nemůžeš-li běžet, jdi, nemůžeš-li ani jít, plaz se. Ale ať už děláš cokoli, musíš se neustále pohybovat kupředu.",
    "Když prohrajete, nezapomeňte na tu lekci.",
    "V podnikání nemůžete čekat, až bouřka přejde, je nutné naučit se tančit v dešti.",
    "Život je někdy velmi skoupý, uplynou dny, týdny, měsíce a roky, aniž člověk zažije něco nového. Ale pak se otevřou dveře a dovnitř se vřítí lavina. V jednu chvíli nemáte nic, a najednou máte víc, než dokážete přijmout.",
    "Svět patří těm, co se neposerou.",
    "Obyčejný člověk přemýšlí, jak by zaplnil čas. Talentovaný člověk se ho snaží využít.",
    "Jestli najdeš v životě cestu bez překážek, určitě nikam nevede.",
    "Pamatuj, že i ta nejtěžší hodina ve tvém životě, má jen 60 minut.",
    "Je zhola zbytečné se ptát, má-li život smysl či ne. Má takový smysl, jaký mu dáme.",
    "Jsem něžný, jsem krutý, ale jsem život. Pláčeš? I v slzách je síla. Tak jdi a žij.",
    "První krok proto, abyste od života získali to, co chcete je rozhodnout se, co to je.",
    "Otázkou není, zda mít nebo nemít pasivní příjem. Otázkou je kdy ho budete mít?",
    "Budoucnost patří těm, kdo věří svým krásným snům.",
    "Vše, co je v člověku krásné, je očima neviditelné.",
    "Žij každý den, jako bys právě v něm měl prožít celý svůj život.",
    "Pro život, ne pro školu se učíme.",
    "Špatné věci nejsou to nejhorší, co se nám může stát. Ta nejhorší věc, která se nám může stát, je NIC.",
    "Nenáviděl jsem každou minutu tréninku, ale vždy jsem si říkal: Teď protrpíš trénink a žij zbytek života jako mistr.",
    "Neselhal jsem 10000 krát. Našel jsem 10000 způsobů, které nefugují.",
    "Všimli jste si, že ti nejchytřejší žáci ve škole nejsou těmi, kterým se daří v životě.",
    "Nikdo se mě neptal jestli se chci narodit, tak ať mi neříká jak mám žít.",
    "Dělejte to, z čeho máte strach. A dělejte to opakovaně. To je nejrychlejší a nejjistějších způsob, jak strach porazit.",
    "Špatná zpráva je ta, že čas letí. Dobrá zpráva je ta, že vy jste pilot.",
    "Včerejšek je tentam, zítřek nám není znám, ale dnešek to je dar. Tak si toho daru náležitě važ.",
    "Život je jako mrdka. Občas prostě musíš polknout.",
    "Vzpomeň si na to, že i zkurvená tlustá panda se stala Dračím bojovníkem, tak drž hubu kurva a začni se snažit, ty líná mrdko.",
    "Řím nebyl postavený za den. Ani za týden. Ale za přesně 1229 let. Takže se na to můžeš vymrdat rovnou.",
    "Najdi si tři koníčky, které miluješ: Jeden, díky kterému si vyděláš peníze. Druhý, díky kterému budeš ve formě.Třetí, díky kterému budeš kreativní.",
    "Dávej si cíle. Nemluv o nich. Začni je tiše plnit. A nakonec si pořádně zatleskej.",
    "Občas prostě potřebuješ pořádný péro a masivní koule.",
    "Každý je génius, ale pokud budete posuzovat rybu podle její schopnosti vylézt na strom, bude celý svůj život žít s vědomím, že je neschopná.",
    "I děvka byla jednou panna.",
    "Občas se musíš rozejít se svou partnerkou se slovy 'Sorry kotě, ale máš na mě moc malý pasivní příjem.'",
    "Když je ti smutno, když je ti zle... Možná je na čase opustit Adastru.",
    "Péro a koule.",
    "Když nevíš, jak na to, tak pomůže lajna párna.",
    "Kdo nesmaží s náma, smaží proti nám."]

LINUX_COPYPASTA = '''
I'd just like to interject for a moment. What you're refering to as Linux, is in fact, GNU/Linux, or as I've recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX.

Many computer users run a modified version of the GNU system every day, without realizing it. Through a peculiar turn of events, the version of GNU which is widely used today is often called Linux, and many of its users are not aware that it is basically the GNU system, developed by the GNU Project.

There really is a Linux, and these people are using it, but it is just a part of the system they use. Linux is the kernel: the program in the system that allocates the machine's resources to the other programs that you run. The kernel is an essential part of an operating system, but useless by itself; it can only function in the context of a complete operating system. Linux is normally used in combination with the GNU operating system: the whole system is basically GNU with Linux added, or GNU/Linux. All the so-called Linux distributions are really distributions of GNU/Linux!
'''
GIDS = [276720867344646144]
TWITTERPERO = 1042052161338626128