# Time to Spare — specyfikacja produktu i implementacji

**Wersja dokumentu:** 1.0<br>
**Data:** 2026-11-04<br>
**Właściciel produktu:** Michał<br>
**Status:** specyfikacja do implementacji; produkt, integracje i wyniki nie zostały jeszcze zwalidowane<br>
**Robocza nazwa repozytorium:** `time-to-spare`<br>
**Język produktu:** polski w MVP, struktura przygotowana na angielski<br>
**Charakter projektu:** open source, aplikacja webowa mobile-first, backend Python, produkt wykorzystujący AI i deterministyczne planowanie

> Ten dokument jest głównym kontekstem dla agenta AI wdrażającego projekt. Opisuje decyzje, kontrakty, kryteria jakości i kolejność pracy. Nie jest poleceniem zbudowania wszystkich etapów naraz. Najpierw należy dostarczyć pierwszy działający przekrój produktu, a następnie przechodzić przez bramki jakości.

## 0. Instrukcja dla agenta implementującego

Przeczytaj cały dokument przed projektowaniem architektury. Sprawdź instrukcje istniejącego repozytorium i jego stan. Nie nadpisuj cudzych zmian. Jeśli wdrażasz projekt w repozytorium zawierającym inne aplikacje, ustal izolowany katalog projektu zgodny z instrukcjami tego repozytorium.

Zasady interpretacji:

- **MUST** — warunek akceptacji danego etapu; niespełnienie blokuje jego uznanie za gotowy.
- **SHOULD** — domyślna decyzja; odstępstwo wymaga krótkiego ADR, czyli zapisu decyzji architektonicznej.
- **MAY** — opcja, której nie implementuj bez konkretnej potrzeby.
- **P0** — MVP do kontrolowanego pilotażu. **P1** — utwardzenie i publiczna beta. **P2** — rozwój po potwierdzeniu użyteczności.
- Liczby dotyczące SLA, kosztów, czasu odświeżania i jakości w tym dokumencie są **celami lub początkowymi parametrami produktu**, nie osiągniętymi wynikami ani gwarancjami dostawców.
- Nie deklaruj wykonanej integracji, aktualnych danych, rzeczywistych użytkowników lub wyników benchmarku bez dowodu.
- Nie dodawaj funkcji tylko po to, by użyć technologii z ogłoszenia rekrutacyjnego.
- Nie zmieniaj twardych ograniczeń użytkownika w celu wygenerowania atrakcyjniejszego planu.
- Nie nazywaj planu bezpiecznym ani gwarantowanym. Produkt oblicza wykonalność przy określonych danych i założeniach.
- Nie publikuj aplikacji, nie zakładaj płatnych kont, nie kupuj usług i nie kontaktuj się z testerami bez osobnego upoważnienia właściciela. Lokalna implementacja, testy i przygotowanie wdrożenia nie wymagają takiej dodatkowej decyzji.

Pierwsza odpowiedź agenta po przeczytaniu specyfikacji powinna zawierać: rozpoznany stan repozytorium, etap do realizacji, najważniejsze niewiadome i najbliższy mierzalny rezultat. Następnie agent powinien pracować nad tym etapem, nie poprzestawać na opisie planu.

## 1. Produkt w jednym zdaniu

**Time to Spare pomaga wybrać i przeżyć krótkie wyjście w mieście, które mieści się w dostępnym czasie, budżecie i możliwościach użytkownika oraz kończy się powrotem do wskazanego miejsca przed ustaloną godziną.**

Przykład potrzeby:

> „Jestem przy Krakowie Głównym, mam pociąg o 19:40. Chcę coś zjeść i chwilę pospacerować. Mam 45 zł i nie chcę się spieszyć”.

Odpowiedź produktu to maksymalnie trzy policzone warianty z mapą, harmonogramem, kosztem, zapasem czasu i informacją o jakości danych. Użytkownik wybiera jeden, rozpoczyna wyjście i może zmienić plan, gdy pada deszcz, lokal jest zamknięty lub chce już wracać.

W MVP godzinę odjazdu wpisuje użytkownik. Aplikacja nie potwierdza rozkładu pociągu. Nie pobiera lokalizacji w tle i nie obiecuje, że poinformuje o konieczności powrotu, gdy przeglądarka jest zamknięta.

### 1.1. Główna obietnica i jej granice

Obietnica: mniej wyszukiwania, mniej układania trasy ręcznie, czytelna informacja o tym, co mieści się w dostępnym oknie.

Granice: szacunki czasu, niepełne godziny otwarcia, kolejki, pogoda, zmiany dostępności i opóźnienia mogą zmienić sytuację. Produkt musi te ograniczenia pokazywać w kontekście konkretnego planu, a nie chować w regulaminie.

Komunikat prawidłowy:

> „Szacowany powrót do wejścia na dworzec: 19:08. Pociąg: 19:40, według wpisanej przez Ciebie godziny. Zarezerwowaliśmy 20 min na dojście do peronu i wejście do pociągu; pozostaje 12 min dodatkowego zapasu”.

Komunikat niedopuszczalny:

> „Na pewno zdążysz na pociąg”.

### 1.2. Wyróżnik

Produkt koncentruje się na krótkim oknie i warunku powrotu. Oryginalność nie polega na samym czacie, mapie lub generowaniu opisów. Istotne są:

1. Planowanie od nieprzekraczalnej godziny powrotu.
2. Jawne rozdzielenie faktów, szacunków i brakujących informacji.
3. Przeliczanie pozostałej części wyjścia.
4. W przyszłości: szukanie wspólnego miejsca i okna dla osób z różnych miejscowości.
5. Otwarty silnik planowania, zestaw ewaluacyjny i format danych miejskich.

To hipoteza pozycjonowania, nie potwierdzona przewaga konkurencyjna. Istnieją ogólne planery podróży, np. [Waystop](https://waystop.app/); przed publicznym launch aktualizuj analizę konkurencji i testuj konkretną różnicę z użytkownikami.

## 2. Użytkownicy, biznes i walidacja

### 2.1. Segment pierwszej wersji

**Pierwszy segment:** osoba dorosła mająca 45–180 minut w centrum jednego miasta, poruszająca się pieszo i wracająca do określonego wejścia na dworzec.

Potencjalne sytuacje:

- oczekiwanie na pociąg lub spotkanie;
- czas po pracy przed powrotem;
- krótka wizyta w mieście;
- wspólne wyjście dwóch osób, które już znajdują się w tej samej okolicy.

Nie zaczynaj od turystów na tygodniowym urlopie, wszystkich miast Polski ani transportu multimodalnego. Częstotliwość potrzeby u podróżnych może być niska; w pilotażu sprawdzaj też osoby regularnie dojeżdżające.

### 2.2. Jobs to be done

| ID | Potrzeba | Sukces z perspektywy użytkownika |
|---|---|---|
| JTBD-01 | Mam trochę czasu i nie chcę go spędzić na szukaniu | W ciągu kilku minut wybieram realne wyjście |
| JTBD-02 | Mam konkretną godzinę powrotu | Widzę policzony powrót i założenia, bez zgadywania |
| JTBD-03 | Mam mały budżet | Znam koszty i wiem, których nie da się potwierdzić |
| JTBD-04 | Warunki zmieniły się w trakcie | Mogę skrócić wyjście lub wrócić bez zaczynania od zera |
| JTBD-05 | Nie znam miasta | Otrzymuję jasne wejścia, trasę, uzasadnienie wyboru i źródła |

### 2.3. Wartość biznesowa

Na etapie OSS celem jest użyteczność, powtarzalne korzystanie i wiarygodny materiał techniczny. Gwiazdki GitHub nie są główną metryką produktu.

Hipotezy późniejszego modelu przychodów:

- hostowana wersja z wygodą utrzymania, dodatkowymi miastami i planami grupowymi;
- wdrożenie dla hostelu, coworkingu lub organizatora wydarzenia;
- finansowanie społecznościowe i sponsoring utrzymania danych.

Nie wdrażaj płatności, reklam, afiliacji ani płatnego rankingu w P0. Sponsor nie może po cichu zmieniać kolejności rekomendacji. Dostępność kodu i koszty API to oddzielne sprawy; bezpłatny kod nie oznacza bezpłatnego hostingu czy modeli.

### 2.4. Eksperyment przed rozbudową

1. Porozmawiaj — po upoważnieniu właściciela — z 5–8 potencjalnymi użytkownikami o ostatniej rzeczywistej sytuacji, w której mieli takie okno czasowe.
2. Zbierz: sposób rozwiązania problemu, ograniczenia, użyte aplikacje i powód rezygnacji z wyjścia.
3. Przeprowadź co najmniej 5 wyjść z prototypem w jednym mieście, za zgodą uczestników. Zapisuj błędy trasy, czasu i danych.
4. Porównaj planowanie z ich zwykłym sposobem, np. mapami i ręcznym wyszukiwaniem. Nie przypisuj całej różnicy AI.
5. Sprawdź, czy uczestnicy korzystają ponownie przy kolejnej rzeczywistej okazji.

Bramka dalszej inwestycji: przynajmniej 3 z 5 testerów oceniają plan jako przydatny w realnym wyjściu, a przynajmniej 2 chcą ponownie użyć go przy następnej okazji. To mały sygnał jakościowy, nie dowód dopasowania do rynku. Krytyczny błąd logistyczny wymaga naprawy przed kolejnym pilotażem.

### 2.5. Metryki

- Główna: odsetek rozpoczętych wyjść, które użytkownik ocenił jako przydatne i zakończone w swoim oknie czasowym.
- Aktywacja: utworzenie pierwszego planu i kliknięcie „Rozpoczynam”.
- Czas od wejścia do wybrania wariantu.
- Odsetek wyników `no_feasible_plan` wraz z przyczyną.
- Powrót do produktu przy kolejnej okazji; pomocniczo retencja 30-dniowa.
- Odsetek zgłoszonych zamkniętych miejsc, błędnych godzin i niepoprawnych tras.
- Koszt wygenerowanego i zaakceptowanego planu.
- Odsetek planów, które walidator odrzucił przed pokazaniem.

Nie traktuj zamknięcia karty jako ukończenia wyjścia. Brak odpowiedzi oznacza wynik nieznany. Pokazuj licznik odpowiedzi i mianownik każdej metryki. Dane jakościowe zbieraj osobno od surowych śladów lokalizacji.

## 3. Zakres i granice etapów

| Obszar | P0: pilot | P1: beta | P2: po walidacji |
|---|---|---|---|
| Miasto | Kraków, wybrany obszar przy Krakowie Głównym | Kolejne miasto po audycie danych | Pakiety miejskie społeczności |
| Przemieszczanie | Pieszo | Ulepszony routing i profile | Transport publiczny, jeśli dane pozwalają |
| Start i powrót | Wybrane punkty wejść, opcjonalny punkt na mapie w obszarze | Lepsze geokodowanie | Różne miasta startu uczestników |
| Czas | Ręcznie wpisany termin, jawne bufory | Opcjonalne dane rozkładowe | GTFS + GTFS-RT dla wspieranych operatorów |
| Plan | 1–3 miejsca, maks. 3 warianty | Lepsze dopasowanie | Planowanie grupowe |
| Preferencje | Formularz + tekst, oba prowadzą do tego samego modelu | Zapamiętane preferencje opt-in | Uczenie rankingu po zebraniu danych |
| Dane miejsc | 30–50 ręcznie sprawdzonych rekordów | Kontrolowany import i moderacja | Więcej zatwierdzonych źródeł |
| Replan | „Pada”, „zamknięte”, „mam mniej czasu”, „wracam” | Powiadomienia opt-in | Monitoring podczas aktywnej sesji |
| Konto | Gość | Opcjonalne konto | Prywatne grupy |
| AI | Ekstrakcja intencji, retrieval, wyjaśnienie | Mierzony agent z ograniczonymi narzędziami | Modele uczone na odpowiednich danych |

### 3.1. Poza zakresem P0

- sprzedaż biletów, rezerwacje i płatności;
- gwarantowanie przesiadek lub prowadzenie do konkretnego peronu;
- obietnica działania w każdym mieście;
- prognozowanie tłumów i kolejek bez danych;
- turn-by-turn navigation, działanie GPS w tle;
- sieć społecznościowa i dopasowywanie nieznajomych;
- autonomiczne przeglądanie całej sieci przez agenta;
- trening własnego LLM, fine-tuning bez benchmarku i danych;
- mikroserwisy, Kubernetes, rozbudowany event bus;
- automatyczna publikacja zgłoszeń użytkowników w bazie miejsc;
- potwierdzanie dostępności dla osób z ograniczeniami ruchowymi wyłącznie na podstawie trasy pieszej.

## 4. UX i zachowanie produktu

### 4.1. Pierwsze wejście

Strona zaczyna się od pytania „Ile masz czasu i skąd ruszasz?”. Użytkownik widzi wspierany obszar, może wybrać dworzec, punkt na mapie albo dobrowolnie udostępnić pozycję. Brak zgody na lokalizację nie blokuje produktu.

Formularz zbiera: start, cel powrotu, datę i godzinę, typ terminu, budżet, tempo, maksymalny czas chodzenia i zainteresowania. Tekst naturalny jest ułatwieniem. Formularz musi działać przy niedostępnym modelu.

**Typ terminu:**

- `departure`: wpisana godzina odjazdu; odejmij jawny bufor wejścia/dojścia do peronu;
- `arrive_by`: użytkownik ma być przy wskazanym punkcie o tej godzinie; bufor wejścia nie jest dodawany automatycznie.

Przed obliczeniem pokazuj krótką kartę ograniczeń. Niejasne „do siódmej” wymaga ustalenia daty i 07:00/19:00. „Jutro” interpretuj w strefie miasta i pokaż datę. Brakujące dane krytyczne dopytaj w jednym zwięzłym kroku.

### 4.2. Ekran wyniku

Każdy wariant MUST zawierać:

- nazwę zrozumiałą dla człowieka, np. „Krótki spacer i coś do jedzenia”;
- godzinę rozpoczęcia i najpóźniejsze rozpoczęcie, jeśli obliczone;
- listę miejsc z czasem pobytu i przejściami;
- dokładny punkt powrotu, nie tylko napis „dworzec”;
- przewidywany powrót, termin, zarezerwowane bufory i pozostały zapas;
- koszt jako zakres lub kwotę potwierdzoną oraz stan kompletności ceny;
- źródła informacji, czas ostatniej weryfikacji i istotne zastrzeżenia;
- przyciski „Wybieram”, „Zmień”, „Tylko powrót”.

Godziny, ceny i geometria są renderowane z modelu domenowego. Tekst LLM nie jest ich źródłem. Nazwy dostawców, embeddingów i grafów nie należą do głównego interfejsu.

### 4.3. Aktywne wyjście

Po kliknięciu „Rozpoczynam” aplikacja zapisuje wersję planu i actual start time. Jeśli opóźnienie rozpoczęcia unieważnia plan, najpierw przelicza i prosi o wybór aktualnego wariantu.

Użytkownik może oznaczyć przyjście, pominięcie lub zakończenie wizyty. Aktualizacja pozycji jest dobrowolna i tylko w aktywnej aplikacji. Bez nowej pozycji replan korzysta z potwierdzonego punktu lub pyta o aktualny start; nie zgaduje go z harmonogramu.

Replan MUST zachować wykonane etapy, źródło zmian i poprzednią wersję. Nie zmienia godziny powrotu, budżetu ani profilu bez potwierdzenia. Zmiana miękkiej preferencji nie jest zgodą na zmianę twardych ograniczeń.

### 4.4. „Wracam teraz”

To osobny deterministyczny przepływ, niezależny od dostępności LLM. Oblicza powrót z aktualnej potwierdzonej lokalizacji. Jeśli termin nie jest już osiągalny według modelu, pokazuje ten fakt i oszacowanie spóźnienia. Nie sugeruje biegania ani ignorowania zakazów.

### 4.5. Stany, które muszą mieć własny projekt ekranu

`needs_clarification`, `planning`, `ready`, `no_feasible_plan`, `provider_unavailable`, `outside_supported_area`, `stale_plan`, `return_deadline_at_risk`, `offline_snapshot`, `cancelled`.

Offline można czytać ostatnio zapisany plan z widocznym oznaczeniem, że nie jest aktualizowany. Nie cache’uj cudzych kafelków mapowych offline bez odpowiedniej umowy. Lista tekstowa jest pełnoprawną alternatywą mapy.

## 5. Wymagania funkcjonalne i akceptacja

| ID | Priorytet | Wymaganie | Minimalny dowód akceptacji |
|---|---|---|---|
| FR-01 | P0 | Ustrukturyzowanie intencji PL | Zestaw przypadków z potocznym czasem, negacją i brakami |
| FR-02 | P0 | Potwierdzenie ograniczeń | UI pokazuje dokładną datę, kwotę i punkt powrotu |
| FR-03 | P0 | Kandydaci tylko ze wspieranego zbioru | Model nie może dodać nowego `place_id` |
| FR-04 | P0 | Trasa po sieci pieszej | Brak użycia odległości w linii prostej jako czasu dojścia |
| FR-05 | P0 | Otwarcie przez cały pobyt | Testy zamknięcia przed końcem wizyty, świąt i przerw |
| FR-06 | P0 | Budżet bez ukrytych kosztów obowiązkowych | Suma górnych granic lub jawna niewykonalność |
| FR-07 | P0 | Powrót z buforami | Niezależny walidator odrzuca naruszenie choćby o sekundę |
| FR-08 | P0 | Plan 1–3 przystanków | Dopuszczalne mniej miejsc, bez sztucznego wypełniania czasu |
| FR-09 | P0 | Replan zachowujący historię | Nowa wersja nie nadpisuje starej |
| FR-10 | P0 | Powrót bez AI | Test awarii modelu przy działającym routingu |
| FR-11 | P0 | Każda istotna informacja ma pochodzenie | Cytowanie pola/fragmentu, nie ogólny link do miasta |
| FR-12 | P0 | Odmowa przy braku danych | Model nie zamienia `unknown` w pozytywną odpowiedź |
| FR-13 | P0 | Tryb demo bez płatnych API | Fikcyjne dane oznaczone, bez prowadzenia w realnym terenie |
| FR-14 | P0 | Zgłoszenie błędu | Trafia do moderacji i może wyłączyć miejsce po weryfikacji |
| FR-15 | P1 | Udostępnienie z ograniczoną ważnością | Nie ujawnia dokładnej pozycji ani tokena właściciela |
| FR-16 | P1 | Konto i kasowanie danych | Kontrola własności, cofnięcie dostępu i ścieżka usuwania |
| FR-17 | P2 | Spotkanie grupy z różnych miast | Każdy uczestnik ma osobno zweryfikowaną drogę powrotną |

## 6. Dane, dostawcy i aktualność

### 6.1. Strategia danych P0

Kraków jest decyzją startową ze względu na kontekst właściciela, nie wynikiem potwierdzonego dostępu do kompletnych danych. Przed pilotem wykonaj audyt obszaru: wejścia na dworzec, realne ciągi piesze, 30–50 miejsc, typowe czasy pobytu i pokrycie godzin otwarcia. Jeśli pokrycie jest niewystarczające, zmniejsz obszar zamiast uzupełniać go halucynacjami.

Miejsca powinny być mieszanką bezpłatnych punktów spacerowych i kilku wiarygodnie opisanych opcji płatnych. „Miejsce na posiłek” z nieznaną ceną lub kolejką nie może być obowiązkowym elementem planu z gwarantowanym limitem kosztów i bardzo ciasnym oknem.

Każde pole krytyczne posiada źródło, datę sprawdzenia i zakres obowiązywania. Przechowuj osobno informację podaną przez źródło, normalizację i decyzję redakcyjną. Nie zapisuj `verified=true` na całym miejscu, jeśli sprawdzono tylko adres.

### 6.2. Adaptery

| Adapter | P0 | Warunek integracji produkcyjnej |
|---|---|---|
| `PlaceCatalog` | Zatwierdzony plik danych → PostgreSQL | Źródła i licencje per rekord/pole |
| `RoutingProvider` | openrouteservice jako kandydat, adapter + fake | Sprawdzone profile, obszar, limity i warunki cache |
| `MapProvider` | MapLibre + wybrany dostawca stylu/kafelków | Zgodne użycie i atrybucja; mapa opcjonalna w demo |
| `GeocodingProvider` | Predefiniowane punkty + wybór na mapie | Komercyjny lub własny backend dopiero przy potrzebie |
| `WeatherProvider` | Ręczna zmiana „Pada” | P1 po wyborze dostawcy i zasad aktualności |
| `TransitProvider` | `ManualDeadlineProvider` | P2; osobno rozkład i realtime |
| `LLMProvider` | Jeden wybrany dostawca + deterministyczny fallback | Structured output, limity, koszty, polityka danych |
| `EmbeddingProvider` | Model wielojęzyczny wybrany przez mały benchmark | Zapis identyfikatora, wymiaru i licencji |

openrouteservice udostępnia m.in. routing, macierze czasów i izochrony. Adapter powinien pobierać macierz dla ograniczonego zbioru kandydatów oraz geometrię dla finalnych wariantów. Nie hardkoduj limitów konta na podstawie przypadkowych tutoriali. [Oficjalna dokumentacja openrouteservice](https://giscience.github.io/openrouteservice/api-reference/).

**Nie używaj publicznego Nominatim jako domyślnego backendu wyszukiwarki aplikacji.** Publiczna usługa ma ograniczenia użycia, wymogi cache i identyfikacji klienta oraz szczególne zasady dotyczące generowanych integracji. P0 nie wymaga geokodowania dowolnego adresu; później wybierz świadomie dostawcę lub własną instancję. [Polityka Nominatim](https://operations.osmfoundation.org/policies/nominatim/).

Otwarte dane OSM nie oznaczają nieograniczonego darmowego serwera map. Publiczne kafelki mają politykę użycia i brak gwarantowanego SLA. Nie planuj na nich bulk download ani domyślnej mapy offline. [Polityka kafelków OSM](https://operations.osmfoundation.org/policies/tiles/).

### 6.3. Rejestr źródeł i prawa do danych

Dla źródła wymagane są: właściciel, URL, typ, licencja/warunki, dozwolony sposób pobierania, cache TTL, wymagane oznaczenie autorstwa, możliwość redystrybucji i status przeglądu.

Źródła z `rights_status=unknown` nie mogą być automatycznie publikowane jako dataset OSS. Nie kopiuj masowo opisów, zdjęć ani opinii z serwisów komercyjnych. Preferuj własne krótkie opisy, dane z odpowiednią licencją i linki do źródeł. Ograniczenia danych, kodu modelu i wag modelu sprawdzaj osobno. Dokument nie stanowi potwierdzenia zgodności prawnej produktu; przegląd warunków dostawców jest bramką publikacji.

Import nie może przerywać obsługi obecnej wersji: `fetch → validate → normalize → review → publish snapshot`. Błędny import pozostawia poprzedni snapshot. Usunięte lub wycofane rekordy są oznaczane i wyłączane z nowych planów.

### 6.4. Polityka aktualności — wartości startowe

| Pole | Próg ponownej weryfikacji | Zachowanie po przekroczeniu |
|---|---|---|
| Podstawowe godziny otwarcia | 7 dni | Wyklucz obowiązkową wizytę wewnątrz w trybie ścisłym |
| Wyjątki świąteczne | Dla konkretnej daty, jeśli dotyczy | Nie zakładaj godzin standardowych |
| Cena obowiązkowa | 7 dni | `unknown`, chyba że źródło ma jawny okres ważności |
| Punkt wejścia i opis | 90 dni | Oznacz do audytu; krytyczna niepewność blokuje |
| Trasa piesza | Do 24 h, zgodnie z warunkami dostawcy | Odśwież przed rozpoczęciem; przy awarii pokaż snapshot |
| Pogoda P1 | 30 min, odpowiedni horyzont | Nie opisuj jako aktualnej |
| GTFS-RT P2 | Domyślnie 120 s, dostosuj do feedu | Przejdź jawnie na rozkład albo odmów danego scenariusza |

To założenia operacyjne, nie gwarancja prawdziwości. `retrieved_at` oznacza pobranie, a `verified_at` faktyczne sprawdzenie. Pobranie starej strony dzisiaj nie czyni ceny aktualną. Każdy rekord ma też `valid_from`, `valid_to` lub jawny brak takiej informacji.

### 6.5. Godziny, święta i ceny

Godziny przechowuj jako lokalny tygodniowy harmonogram z wyjątkami datowymi, ostatnim wejściem, przerwami i strefą IANA. Przedział pobytu musi w całości mieścić się w dostępnym przedziale. Jeśli wyjątków świątecznych nie uda się ustalić, status wynosi `unknown`, nie `open`.

Punkt plenerowy nie jest automatycznie dostępny 24/7. Park może mieć bramy, a punkt widokowy ograniczenia. Brak pola godzin nie jest potwierdzeniem całodobowości.

Koszty zapisuj w najmniejszych jednostkach waluty, w P0 PLN/grosze. Rozdziel koszty obowiązkowe, opcjonalne i zależne od zamówienia. W restauracji pokaż cenę konkretnej zweryfikowanej opcji lub zakres z założeniami. Nie reklamuj „posiłku za 20 zł”, jeśli kwota dotyczy wyłącznie napoju.

## 7. Architektura i technologia

### 7.1. Decyzja bazowa

**Modularny monolit z jednym repozytorium, backendem API i procesem workera.** Frontend jest osobną aplikacją w tym samym repozytorium. Wspólny PostgreSQL. Bez rozdzielania domen na serwisy przed wykazaniem potrzeby.

| Warstwa | Decyzja | Uzasadnienie |
|---|---|---|
| Backend | Python 3.12+, FastAPI, Pydantic v2 | Typowane kontrakty, walidacja, dobry ekosystem AI |
| Pakiety Python | `uv`, lockfile | Powtarzalne środowisko |
| Baza | PostgreSQL 16+ + PostGIS + pgvector | Relacje, geografia i wektory bez trzech osobnych baz |
| ORM i migracje | SQLAlchemy 2, Alembic | Jawne migracje i transakcje |
| Jobs | Celery + Redis; jobs zapisane również w PostgreSQL | Retry i procesy tła; Redis nie jest źródłem prawdy |
| Orkiestracja AI | LangGraph w warstwie aplikacyjnej | Jawny przepływ, checkpointy i ograniczone narzędzia |
| Planner | Czysty Python, enumeracja/pruning w MVP | Mały zakres, przewidywalność, łatwe testowanie |
| Frontend | React + TypeScript strict + Vite | Lekka aplikacja bez potrzeby SSR |
| UI | Tailwind CSS, dostępne komponenty, TanStack Query | Spójność i kontrola stanu serwerowego |
| Mapa | MapLibre GL JS | Otwarty renderer; źródło map niezależne |
| Testy | pytest, Hypothesis, Playwright, Vitest | Własności planera, API, UI, E2E |
| Obserwowalność | OpenTelemetry, metryki i strukturalne logi | Diagnostyka bez przywiązania do jednej usługi |
| Dev/deploy | Docker Compose; kontenery z healthchecks | Mały koszt wejścia i prosty hosting |
| CI | GitHub Actions | Testy, skany, build, ewaluacje |

Wersje są minimalnymi liniami projektowymi, nie instrukcją instalacji „latest”. Przy implementacji sprawdź kompatybilność, przypnij konkretne wersje i obrazy, zapisz je w lockfile oraz ADR. Zbuduj i przetestuj obraz PostgreSQL obsługujący obie wymagane wtyczki; nie zakładaj, że dowolny obraz pgvector zawiera PostGIS.

PostGIS może służyć do przestrzennego prefiltra; odległości `geography` w `ST_DWithin` są w metrach. Nie używaj stopni długości geograficznej jako metrów. [Dokumentacja ST_DWithin](https://postgis.net/docs/ST_DWithin.html). pgvector obsługuje wyszukiwanie podobieństwa w PostgreSQL; przy małym katalogu zacznij od dokładnego wyszukiwania, dopiero po pomiarze rozważ indeks przybliżony. [Dokumentacja pgvector](https://github.com/pgvector/pgvector).

### 7.2. Granice modułów

```text
Web UI
  → API / application services
      → intent + preferences
      → place retrieval
      → itinerary planner
      → independent plan validator
      → session / replan
      → evidence / explanation
      → jobs / integrations
          → PostgreSQL (PostGIS, pgvector)
          → Redis + worker
          → routing / LLM / source adapters
```

Domena nie importuje FastAPI, LangGraph, klienta LLM ani SDK routingu. Planner przyjmuje już ustrukturyzowane dane i macierz tras. Ten sam planner musi działać z fixture’ami bez sieci.

LangGraph nie zastępuje kolejki zadań. Celery dostarcza zadanie, LangGraph organizuje kroki konkretnego runu, PostgreSQL przechowuje stan biznesowy. Przy wznowieniu sprawdź aktualność czasu i danych; zapisany checkpoint nie potwierdza, że wczorajsza trasa jest nadal wykonalna. [Dokumentacja trwałości stanu LangGraph](https://docs.langchain.com/oss/python/langgraph/persistence).

### 7.3. Struktura docelowego repozytorium

```text
apps/api/src/time_to_spare/
  domain/           # constraints, time, money, itinerary, evidence
  application/      # use cases, authorization, orchestration
  planning/         # candidate search, solver, independent validator
  ai/               # intent, prompts, graph, structured output
  infrastructure/   # database, provider clients, jobs
  http/             # routes, request/response schemas
apps/web/src/
  features/         # request, results, active-trip, feedback
  components/
  api/              # generated client
packages/contracts/ # OpenAPI snapshot, generated TS types
citypacks/          # schemas and only redistributable data
fixtures/           # explicitly synthetic demo cases
benchmarks/         # cases, labels, runner, reports
infra/              # images, compose, deployment examples
docs/               # ADRs, product, data sources, operations
```

Nazwy katalogów można dopasować do istniejącego repozytorium. Granice odpowiedzialności należy zachować.

## 8. Model domenowy i przechowywanie

### 8.1. Najważniejsze encje

| Encja | Pola kluczowe |
|---|---|
| `CityPack` | id, version, timezone, service polygon, dataset snapshot, status |
| `ReturnPoint` | id, name, entrance coordinates, buffer policy, evidence |
| `Place` | id, city, canonical name, categories, entrance geography, status |
| `PlaceFact` | place, field, typed value, source id, validity, verified time, confidence state |
| `OpeningSchedule` | timezone, weekly intervals, exceptions, last admission, provenance |
| `PriceOption` | currency, min/max minor units, mandatory/optional, description, validity |
| `VisitProfile` | min/typical/max duration, indoor/outdoor, source of estimate |
| `SourceDocument` | URL, rights, hash, retrieved/verified timestamps, source kind |
| `EvidenceChunk` | source, place, text/span, language, validity, embedding model/version |
| `PlanningRequest` | session, confirmed constraints, original timezone, created time |
| `PlanningRun` | job id, input hash, versions, state, usage, errors, trace id |
| `PlanVersion` | plan id, version, parent, immutable inputs, status, validation report |
| `PlanStop` | order, place snapshot, arrival/start/end, visit duration, cost, evidence |
| `RouteLeg` | origin/destination entrances, duration, distance, geometry, provider snapshot |
| `TripSession` | owner, chosen version, status, progress, last confirmed location/time |
| `Feedback` | session/plan/place ref, category, voluntary comment, moderation status |
| `ShareLink` | hashed capability, expiry, scope, revoked time; P1 |
| `OutboxEvent` | event type, payload reference, state, retries |

### 8.2. Reguły zapisu

- UUID jako identyfikatory. Wszystkie rekordy użytkownika mają właściciela lub sesję i kontrolę dostępu.
- Czas zdarzeń jako `timestamptz` w UTC; zachowuj osobno strefę IANA i lokalną datę podróży.
- Waluty jako integer minor units. Współrzędne WGS84; jawna kolejność: API `lat/lon`, GeoJSON `[lon, lat]`.
- `unknown` i `false` są różnymi wartościami. Nie zamieniaj braku ceny na zero.
- PlanVersion jest niemutowalny. Zmiana tworzy kolejną wersję i unieważnia poprzedni wybór do czasu potwierdzenia.
- Snapshot planu wskazuje wersję danych, algorytmu, polityki buforów, modelu, promptu i źródła routingu.
- Indeksy: GiST na geometrii/geography, B-tree na owner/status/time, unikalny klucz idempotencji, full-text index; wektorowy dopiero po pomiarze.
- Czas ważności wektorów jest związany ze źródłem. Wycofany dokument musi zniknąć z retrieval bez oczekiwania na pełny reindex.
- Wybór modelu embeddingów określa wymiar. Zmiana modelu tworzy nową generację indeksu; nie mieszaj przestrzeni wektorowych.

## 9. Silnik planowania — najważniejsza część produktu

### 9.1. Twarde i miękkie warunki

**Twarde:** termin, dopuszczalny obszar, tryb pieszy, zadany maksymalny dystans/czas chodzenia, budżet w trybie ścisłym, zakazy użytkownika, potwierdzone wymagania dostępności, brak zamkniętych miejsc.

**Miękkie:** różnorodność, preferowana kategoria, mniej tłumów bez gwarancji, estetyka trasy, stopień nowości, preferowany czas pobytu ponad minimum.

`prefer_indoor` może być miękkie. „Nie chcę wychodzić na deszcz” powinno prowadzić do wyjaśnienia, że trasy piesze zawierają odcinki na zewnątrz; system nie może udawać pełnej ochrony.

### 9.2. Czas i bufory

Definicje:

```text
T0 = potwierdzony start wyjścia
D  = termin wpisany przez użytkownika
B_board = bufor od wejścia na dworzec do wejścia do pociągu
B_reserve = dodatkowy zapas operacyjny
D_site = D - B_board        (dla deadline_type=departure)
D_site = D                  (dla deadline_type=arrive_by)
D_plan = D_site - B_reserve
```

Domyślne parametry P0 do pilotażu: `B_board=20 min` dla wpisanego odjazdu z Krakowa Głównego, `B_reserve=10 min`. Są to **heurystyki produktu**, nie pomiary dworca. Pokazuj je użytkownikowi; możliwość korekty jest jawna, nie może być automatyczną metodą „naprawienia” planu. Minimalne dopuszczalne wartości stanowią konfigurację polityki z uzasadnieniem.

Przejście `i→j`:

```text
walk_seconds = ceil(provider_duration_seconds * pace_multiplier
                    * route_uncertainty_multiplier)
```

Początkowo tempo standardowe `1.0`, spokojne `1.25`; rezerwa niepewności trasy `1.15`. Nie nazywaj ich przedziałem ufności ani percentylem bez danych. Nie dodawaj ponownie tej samej rezerwy, jeśli profil dostawcy już ją uwzględnia — kontrakt adaptera definiuje znaczenie zwracanej wartości.

Dla miejsca j:

```text
arrival_j = departure_i + walk_seconds(i, j)
start_j = najwcześniejsza chwila >= arrival_j,
          dla której cały pobyt mieści się w jednym otwartym przedziale
end_j = start_j + dwell_seconds_j
```

Uwzględnij last admission, oczekiwanie na otwarcie, ograniczenia daty i kolejki, jeśli istnieją wiarygodne dane. W P0 bez danych o kolejce stosuj jawny bufor pobytu lub wyłącz wizytę wymagającą wejścia w ciasnym planie. Nie deklaruj liczby osób ani aktualnego czasu obsługi bez źródła.

Końcowy warunek: `arrival_return <= D_plan`. Renderuj osobno `arrival_return`, `D_site`, `B_reserve`, `B_board` i dodatkowy zapas. Nie sumuj bufora wejścia dwa razy.

### 9.3. Przykład obliczeniowy — syntetyczny

```text
Start: 17:40
Wpisany odjazd: 19:40
Bufor dworcowy: 20 min → D_site=19:20
Rezerwa: 10 min        → D_plan=19:10

Dojście 12 min → punkt A 17:52
Pobyt 20 min  → wyjście 18:12
Dojście 8 min → punkt B 18:20
Pobyt 25 min  → wyjście 18:45
Powrót 18 min → wejście na dworzec 19:03

Dodatkowy zapas do D_plan: 7 min
Łącznie do odjazdu: 37 min = 7 + 10 + 20
```

Czasy przejść w przykładzie już zawierają mnożniki. To fixture edukacyjny, nie rzeczywista trasa w Krakowie.

### 9.4. Algorytm P0

1. Waliduj input i potwierdź godzinę startu; odrzuć termin w przeszłości.
2. Sprawdź wspierany polygon oraz dostępność startu i punktu powrotu.
3. Oblicz trasę bezpośredniego powrotu. Jeśli nawet ona nie spełnia terminu, nie proponuj atrakcji.
4. Wybierz kandydatów przez twardy prefiltr geograficzny i warunki danych.
5. Dodaj ranking semantyczny i leksykalny, zachowując różnorodność kategorii. Początkowo maks. 20 kandydatów.
6. Pobierz macierz pieszą dla startu, kandydatów i powrotu, z podziałem na batche zgodne z limitem dostawcy.
7. Enumeruj uporządkowane sekwencje 1–3 różnych miejsc. Dla 20 kandydatów liczba jest mała; pruning odrzuca częściowe ścieżki bez możliwego powrotu.
8. Dla każdej sekwencji wyznacz wizyty, oczekiwanie, koszty i powrót. Odrzuć każdy konflikt twardy.
9. Oceniaj tylko wykonalne plany. Wybierz do trzech istotnie różnych wariantów.
10. Pobierz finalne geometrie tras. Jeśli ich czasy różnią się od macierzy, przelicz harmonogram i waliduj ponownie.
11. Niezależny walidator sprawdza finalny artefakt. Dopiero potem generuj wyjaśnienie i renderuj odpowiedź.

Warunek wyboru trzech wariantów nie może wymuszać dodawania niewykonalnych lub prawie identycznych tras. Zero wariantów jest poprawnym wynikiem.

### 9.5. Ranking

Początkowy score jest jawny i konfigurowalny:

```text
score = preference_match + category_diversity + useful_visit_time
        - walking_burden - waiting_burden - data_uncertainty_penalty
```

Składniki znormalizowane do porównywalnego zakresu; wagi zapisane w wersjonowanej konfiguracji. `return_slack` może rozstrzygać remis, lecz nie premiuj bez końca pustych planów. Warianty różnicuj np. „najspokojniej”, „jedzenie i spacer”, „najwięcej oglądania”, ale każdy przechodzi ten sam zestaw twardych reguł.

Nie generuj „92% pewności, że zdążysz”. W P0 pokazuj zapas minut i jakość danych. Kalibrację probabilistyczną można wprowadzić dopiero po zebraniu reprezentatywnych obserwacji.

### 9.6. Budżet

W trybie ścisłym suma górnych granic kosztów obowiązkowych nie może przekroczyć limitu. Cena nieznana wyklucza obowiązkowy zakup. Opcjonalne zakupy mogą być pokazane poza kosztem bazowym z jasnym oznaczeniem.

W planowaniu grupowym ceny per osoba i per grupa są osobnymi polami. Nie implementuj tego przez mnożenie wszystkich kosztów przez liczbę uczestników.

### 9.7. Brak planu

Zwróć konkretne kody: `INSUFFICIENT_TIME`, `RETURN_UNREACHABLE`, `OPENING_HOURS_UNKNOWN`, `NO_OPEN_PLACES`, `BUDGET_UNSATISFIABLE`, `ROUTING_UNAVAILABLE`, `ACCESSIBILITY_UNVERIFIED`, `OUTSIDE_COVERAGE`.

Można zaproponować: mniej miejsc, tylko spacer, większy budżet lub inny termin. Zmiana warunku twardego wymaga akcji użytkownika. Nie pokazuj „po prostu zdążysz szybciej”.

### 9.8. Replan i konkurencyjne zmiany

Replan bierze aktualny czas, potwierdzoną pozycję, wykonane wizyty, poniesione wydatki i pozostały budżet. Chroni bazową wersję przez optimistic concurrency. Dwa równoległe replany nie mogą nadpisać się bez kontroli; nieaktualny `base_version` daje konflikt 409.

Nowy plan jest propozycją. Dopiero zatwierdzenie zmienia `active_plan_version`. Jeśli warunki nie pozwalają na dalszą aktywność, priorytetem jest wynik powrotu. Gdy powrót przekracza termin, pokaż rzeczywisty stan, nie przywracaj pozornie zielonego statusu.

## 10. AI: odpowiedzialność, RAG i kontrola wykonania

### 10.1. AI może i nie może

AI może:

- wyciągać intencję z wypowiedzi i wskazywać niejednoznaczności;
- wyszukiwać semantycznie pasujące miejsca w zatwierdzonym katalogu;
- wybierać dozwolone narzędzie w ograniczonym przepływie;
- wyjaśniać różnice między zwalidowanymi wariantami;
- streszczać źródłowe fakty z cytowaniem.

AI nie może:

- wymyślać miejsca, ceny, godzin, połączenia lub czasu przejścia;
- ustalać wykonalności przez tekstowe rozumowanie;
- zmieniać ograniczeń użytkownika bez potwierdzenia;
- wykonywać dowolnego kodu, odwiedzać dowolnego URL ani dokonywać rezerwacji;
- traktować instrukcji ze źródłowego opisu jako poleceń systemowych;
- zastępować niezależnego walidatora drugim promptem typu „sprawdź, czy dobrze”.

### 10.2. Przepływ grafu

```text
RECEIVED
  → PARSE_INTENT
  → VALIDATE_CONSTRAINTS
      → NEEDS_CLARIFICATION → oczekiwanie na potwierdzenie
      → RETRIEVE_CANDIDATES
  → LOAD_FACTS_AND_ROUTES
  → SOLVE
  → VALIDATE_PLAN
      → NO_FEASIBLE_PLAN / PROVIDER_UNAVAILABLE
      → EXPLAIN_WITH_EVIDENCE
  → VALIDATE_EXPLANATION
  → READY
```

W P0 graf jest przede wszystkim kontrolowanym workflow. Nie nazywaj go systemem wieloagentowym. P1 może dodać ograniczoną decyzję agenta: np. uzupełnienie konkretnego faktu z zatwierdzonego źródła lub pobranie innego zestawu kandydatów. Każdy krok musi mieć mierzalny cel.

Dozwolone narzędzia są wąskie: `search_places`, `read_place_facts`, `compute_route_matrix`, `solve_itinerary`, `validate_itinerary`, `explain_plan`. Operacje odczytu źródeł działają przez backend z allowlistą, nie przez swobodny browser agenta.

Limity początkowe na run: 2 standardowe wywołania LLM — ekstrakcja i wyjaśnienie — oraz maksymalnie 1 naprawa schematu na etap. Maks. 4 wywołania łącznie. Cały run ma deadline i budżet; retry nie resetuje licznika. Po przekroczeniu limitu użyj formularza/wyjaśnienia szablonowego lub zwróć jawny błąd.

### 10.3. Retrieval

Kolejność: uprawnienia i obszar → aktualność → twarde filtry → lexical + vector retrieval → opcjonalny reranking → fakty → solver.

Embedding opisuje cechy miejsca, nie zastępuje rekordów ceny i godzin. Chunkowanie według sekcji i obiektu, z małą ilością nakładania, jeśli potrzebne. Każdy chunk wskazuje wersję dokumentu, język, miejsce i zakres tekstu. Wielkości chunków dobierz pomiarem, a nie dogmatem „zawsze 512 tokenów”.

Baseline dla katalogu 30–50 miejsc: tagi + wyszukiwanie leksykalne. Dodanie wektorów ma sens, jeśli poprawia przypadki typu „spokojny zakątek”, „coś pod dachem bez zakupów”. Jeśli nie poprawia jakości w tym zbiorze, nie wymuszaj go w krytycznej ścieżce. Zachowaj moduł do porównania i uczciwie opisz wynik.

Reranker dopiero po pomiarze. Model embeddingów wybierz spośród wielojęzycznych kandydatów na własnym zbiorze PL; porównaj jakość, latency, pamięć i licencję. Zapisz model ID, revision, wymiar, normalizację i metrykę odległości.

### 10.4. Fakty i cytowania

Output wyjaśnienia powinien zawierać strukturę `claims[]`: tekst, lista `fact_ids`, lista `evidence_ids`. Walidator sprawdza, że identyfikatory należą do bieżącego snapshotu i dopuszczonego kontekstu. Liczby i godziny są wstawiane przez renderer z planu.

Samo istnienie cytowania nie dowodzi, że wspiera ono treść. Sprawdzaj pokrycie faktów regułami, audytem ludzkim i pomocniczą oceną modeli. Przy niepewnym uzasadnieniu pokaż neutralny szablon oparty wyłącznie na zatwierdzonych cechach.

### 10.5. Wybór LLM i rozwój ML

Nie przypisuj na stałe „najlepszego modelu”. Przed zamknięciem milestone’u porównaj przynajmniej dwa dostępne warianty na tym samym holdoucie i z tymi samymi limitami. Zapisz koszty z aktualnego cennika dostawcy, czas odpowiedzi, jakość PL i odsetek błędnego JSON.

P0 uczy produkcyjnej inżynierii GenAI. Nie stanowi samo w sobie doświadczenia w trenowaniu modeli. Sensowne zadanie ML na później: ranking wariantów po uzyskaniu odpowiedniej liczby dobrowolnych ocen. Porównuj go z prostą heurystyką, rozdziel dane po użytkownikach i czasie, kontroluj cold start i bias popularnych miejsc. Bez danych nie twórz pozornej personalizacji.

## 11. Kontrakty API

### 11.1. Zasady

REST, JSON, `/api/v1`, OpenAPI generowane z modeli. Frontend używa generowanego klienta. Czas ISO 8601 z offsetem plus strefa IANA; odrzuć konflikt offsetu i strefy dla podanej daty. Walidacja serwera jest nadrzędna wobec frontendu.

Długie operacje zwracają `202 Accepted` i `run_id`. Frontend odpytuje status z backoff; SSE może być dodane w P1. Nie utrzymuj blokującego połączenia HTTP przez cały plan.

### 11.2. Endpointy

| Metoda i ścieżka | Cel |
|---|---|
| `GET /cities` | Zasięg i status wspieranych pakietów |
| `GET /cities/{id}/return-points` | Potwierdzone punkty wejść/powrotu |
| `POST /guest-sessions` | Utworzenie sesji gościa i ustawienie bezpiecznego cookie |
| `POST /intents/parse` | Ekstrakcja tekstu do propozycji formularza |
| `POST /planning-runs` | Potwierdzone ograniczenia → zadanie planowania |
| `GET /planning-runs/{id}` | Stan, ewentualne pytania lub identyfikatory wariantów |
| `GET /plans/{id}/versions/{version}` | Niemutowalny plan dostępny dla właściciela |
| `POST /trips` | Wybór planu i rozpoczęcie po walidacji aktualności |
| `POST /trips/{id}/progress` | Potwierdzenie lokalizacji/etapu |
| `POST /trips/{id}/replans` | Nowa propozycja względem wskazanej wersji |
| `POST /trips/{id}/accept-plan` | Atomowe zatwierdzenie nowej wersji |
| `POST /trips/{id}/return-route` | Trasa powrotu bez LLM |
| `POST /feedback` | Ocena i zgłoszenie błędu |
| `DELETE /guest-sessions/current` | Usunięcie danych bieżącej sesji według polityki |
| `GET /health/live`, `GET /health/ready` | Stan procesu i zależności |

### 11.3. Przykładowy request — fixture, nie dane wyjścia

```json
{
  "city_id": "krakow-pilot",
  "start": {"kind": "return_point", "id": "fixture-station-entrance"},
  "return_point_id": "fixture-station-entrance",
  "starts_at": "2030-06-11T17:40:00+02:00",
  "timezone": "Europe/Warsaw",
  "deadline": {
    "type": "departure",
    "at": "2030-06-11T19:40:00+02:00",
    "source": "user_entered"
  },
  "budget": {"max_minor": 4500, "currency": "PLN", "mode": "strict"},
  "pace": "relaxed",
  "max_walk_minutes": 60,
  "interests": ["food", "walk"],
  "avoid": ["stairs"],
  "buffer_policy_id": "pilot-v1",
  "constraints_confirmed": true
}
```

Brak potwierdzonej informacji o schodach musi prowadzić do wykluczenia trasy lub komunikatu o braku możliwości sprawdzenia, a nie zapewnienia, że wymóg został spełniony. Fixture powinien mieć zdefiniowany taki przypadek.

### 11.4. Odpowiedzi i błędy

`202`: `run_id`, `status`, `poll_after_ms`, `request_id`.

Gotowy wynik: `plan_ids`, `created_at`, `valid_until`, `data_snapshot_id`, `validation_status`, `warnings`. `valid_until` to techniczny limit ponownego sprawdzenia, nie gwarancja ważności świata rzeczywistego.

Błąd: `code`, `message`, `retryable`, `field_errors`, `suggested_actions`, `request_id`. Bez stack trace i treści promptów.

`422` — niepoprawne pola. `409` — konflikt wersji/idempotencji. `429` — limit. `503` — brak wymaganej zależności. Brak wykonalnego planu jest wynikiem domenowym runu, nie błędem HTTP 500.

### 11.5. Idempotencja i transakcje

`Idempotency-Key` obowiązkowy dla tworzenia planów i replanów. Zakres klucza: właściciel + endpoint, ważność początkowo 24 h. Ten sam klucz i payload zwracają ten sam run; inny payload daje 409.

Zapis runu i eventu kolejki w jednej transakcji przez outbox. Dispatcher może wysłać job ponownie, worker sprawdza status i input hash. Zakładaj at-least-once delivery. Wskaż, które kroki są idempotentne i jak deduplikowane są rachunki/provider calls po przerwaniu procesu. Nie obiecuj exactly-once dla zewnętrznych API; loguj próbę i niepewny status.

## 12. Niezawodność, wydajność i koszty

### 12.1. Cele P1, mierzone przed deklaracją

| Miara | Cel początkowy | Pomiar |
|---|---|---|
| API odczyt własnego planu | p95 < 300 ms po stronie backendu | 20 równoległych sesji, opisane środowisko |
| Generacja planu | p95 < 15 s przy zdrowych zależnościach | Mieszane scenariusze i cache misses |
| Deadline runu | 30 s | Po przekroczeniu fallback lub jawny wynik |
| Trasa powrotu | p95 < 5 s przy działającym routingu | Bez udziału LLM |
| Dostępność API | Cel 99,5% miesięcznie | Osobno zależności i użyteczne odpowiedzi |
| Koszt LLM+embedding per standard run | Budżet projektowy ≤ 0,05 USD | Faktyczne usage, ceny z datą |
| Brak naruszeń twardych reguł | 0 w zestawie akceptacyjnym | Deterministyczny walidator |

Cele nie są gwarancją. Jeśli wybrany model przekracza budżet, zmień model/flow albo udokumentuj zmianę założenia. Koszt całkowity uwzględnia również routing, mapy, bazę i hosting. Nie nazywaj projektu „za darmo”, jeśli jego pełna wersja wymaga kluczy.

### 12.2. Budżety wykonania

Oddziel connect/read timeouts. Maks. 2 retry z jitter wyłącznie dla operacji, które można bezpiecznie powtórzyć, w ramach globalnego deadline’u. Circuit breaker per dostawca. Limity liczby kandydatów i wielkości odpowiedzi. Rate limiting sesji/IP z możliwością konfiguracji i bez przechowywania surowego IP dłużej niż to potrzebne.

Cache kluczowany przez wersję danych, routing profile, współrzędne wejść, model i politykę. Nie cache’uj spersonalizowanego planu wyłącznie po tekście promptu. Oddziel cache współdzielonych faktów od wyników prywatnej sesji. Każdy cache podlega warunkom dostawcy.

### 12.3. Tryby degradacji

| Awaria | Zachowanie |
|---|---|
| LLM | Formularz i szablonowe uzasadnienie nadal działają |
| Embedding | Ranking tagami/leksykalny |
| Routing | Brak nowych planów „wykonalnych”; dostępny oznaczony snapshot |
| Mapa | Lista tekstowa i link do zewnętrznej nawigacji po wyborze użytkownika |
| Źródło godzin | Wykluczenie niepotwierdzonej wizyty w trybie ścisłym |
| Worker | Run widoczny jako opóźniony, recovery i timeout |
| Redis | Zapis outbox w bazie; odroczone wykonanie, brak fałszywego sukcesu |
| PostgreSQL | Kontrolowany błąd; brak zapisu planu wyłącznie w cache |
| Przeglądarka offline | Snapshot z czasem zapisu, bez deklaracji live |

### 12.4. Obserwowalność

Logi strukturalne: request/run id, etap, latency, provider, błąd kategorii, liczba kandydatów, liczba wyników walidacji, cache hit, token usage i wyliczony koszt. Domyślnie bez tekstu użytkownika, dokładnej pozycji i zawartości źródłowych dokumentów.

Metryki: błędy providerów, czas kolejki, czas solvera, powody braku planu, przekroczenia budżetu, odsetek niepoprawnego outputu LLM i użycie fallbacków. Trace obejmuje API → worker → graph → provider, bez sekretów w atrybutach.

Alerty: wzrost 5xx, kolejka powyżej progu, koszt dzienny powyżej budżetu, krytyczny błąd walidatora, nieudany import źródła, zaległa weryfikacja danych. Początkowe progi konfigurowalne i dopasowane po pilotażu.

## 13. Bezpieczeństwo, prywatność i zaufanie

### 13.1. Sesja i uprawnienia

P0 bez konta: losowy token sesji co najmniej 128 bit entropii, cookie `HttpOnly`, `Secure`, odpowiedni `SameSite`, hash tokena po stronie bazy. Używaj same-origin frontendu/API. Zabezpiecz operacje zmieniające stan przed CSRF; sprawdzaj pochodzenie i token, jeśli wymaga tego wybrany model.

Każdy odczyt i zapis planu sprawdza właściciela. UUID nie zastępuje autoryzacji. P1 link udostępnienia to osobny token read-only z datą wygaśnięcia i możliwością cofnięcia. Udostępniony plan nie pokazuje bieżącej pozycji właściciela.

### 13.2. Zagrożenia AI i źródeł

Treści miejsc i feedback są niezaufanymi danymi. Oddziel instrukcje systemowe, input użytkownika i źródła. Model nie posiada bezpośredniego dostępu do sekretów, SQL ani shella. Zweryfikuj schemat i allowlistę identyfikatorów każdej odpowiedzi.

Importer: allowlista domen, blokada adresów prywatnych/localhost/metadata, walidacja DNS i przekierowań, limity rozmiaru i czasu. Ochrona przed SSRF, XSS w opisach i prompt injection. HTML renderowany przez bezpieczny sanitizer; najlepiej przechowywać normalizowany tekst z kontrolowanym markupem.

Bezpieczne konfiguracje logów i tracingu obowiązują również w środowisku developerskim z realnymi danymi. Żaden klucz do LLM/routingu nie trafia do frontendu ani repozytorium. Klucze mapowe publiczne, jeśli dostawca tak je projektuje, ogranicz do domen i wymaganych uprawnień.

### 13.3. Minimalizacja danych i retencja — polityka produktu

- Surowe teksty preferencji: nie przechowuj po ekstrakcji, chyba że użytkownik świadomie zgodzi się na wykorzystanie do ewaluacji.
- Dokładna ostatnia lokalizacja: przechowuj tylko na czas aktywnego wyjścia i maks. 24 h po zakończeniu; historia śladu GPS nie jest zbierana w P0.
- Prywatne sesje i plany gościa: domyślnie 7 dni, możliwość wcześniejszego skasowania.
- Logi techniczne bez danych wrażliwych: 14 dni.
- Dobrowolny feedback: domyślnie 90 dni; anonimizacja przed użyciem jako dataset.
- Backupy: rotacja do 30 dni; usunięcia realizowane również po odtworzeniu przez rejestr tombstones.

To projekt retencji, który wymaga wdrożenia i przeglądu przed publiczną usługą. Nie deklaruj zgodności z RODO samym dodaniem bannera. Dokumentacja prywatności ma wyjaśniać odbiorców danych, retencję, usuwanie i zewnętrzne API; przegląd prawny jest osobną decyzją właściciela.

Do LLM przekazuj tylko informacje potrzebne do zadania: preferencje i wybrane fakty. Dokładna pozycja i identyfikatory użytkownika zazwyczaj nie są potrzebne do generowania wyjaśnienia. Do routingu trafiają współrzędne niezbędne do wyznaczenia trasy.

### 13.4. Dostępność i bezpieczeństwo trasy

Interfejs projektuj z celem WCAG 2.2 AA: klawiatura, czytelny kontrast, etykiety, focus, alternatywa tekstowa mapy, brak komunikatów opartych tylko na kolorze. Przed deklaracją zgodności wykonaj audyt; automatyczny skaner nie wystarcza.

Routing pieszy nie oznacza trasy odpowiedniej dla wózka, osoby niewidomej lub osoby z ograniczoną sprawnością. Jeśli użytkownik poda takie wymaganie, a pokrycie danych jest niewystarczające, nie oferuj zapewnienia. Wyklucz znane przejścia prywatne i zamknięte; nie oceniaj bezpieczeństwa dzielnic na podstawie generowanych opinii.

## 14. Testy i ewaluacja

### 14.1. Piramida testów

1. Testy jednostkowe domeny: czas, koszty, okna otwarcia, ograniczenia, stan sesji.
2. Testy własności planera z Hypothesis.
3. Testy integracyjne z prawdziwym PostgreSQL + PostGIS + pgvector w kontenerze.
4. Testy kontraktowe adapterów na zapisanych, zanonimizowanych i dozwolonych fixture’ach.
5. Testy E2E ścieżek użytkownika w Playwright.
6. Osobny benchmark AI: extraction, retrieval, grounding i odporność na brak danych.
7. Kontrolowane testy terenowe przed deklaracją użyteczności.

Nie mierz jakości wyłącznie coverage ani oceną LLM-as-a-judge. Każdy krytyczny przypadek regresji otrzymuje test związany z konkretnym błędem.

### 14.2. Własności planera

- Każdy zaakceptowany plan wraca nie później niż `D_plan`.
- Każdy pobyt mieści się w dostępności miejsca i respektuje last admission.
- Suma kosztów obowiązkowych nie przekracza limitu w trybie strict.
- Czasy są monotoniczne; brak ujemnych wizyt, teleportacji i nakładających się etapów.
- Zwiększenie kosztu pojedynczego elementu nie może pozostawić planu pod budżetem, jeśli suma go przekroczyła.
- Skrócenie deadline’u nie czyni wcześniej niewykonalnej **tej samej sekwencji** wykonalną.
- Zwiększenie bufora nie zwiększa zbioru wykonalnych sekwencji przy stałych pozostałych danych.
- Wynik nie zawiera wycofanego miejsca, nieznanego ID ani źródła z innego snapshotu.
- Replan nie cofa zakończonego etapu i nie wydaje ponownie już wydanych pieniędzy jako dostępnego budżetu.
- Powtórzenie z tymi samymi danymi, seedem i konfiguracją daje ten sam wynik solvera.

Walidator sprawdza finalny plan niezależnie od sposobu jego wygenerowania. Nie powinien tylko powtarzać wywołania solvera i uznawać jego flagi za dowód.

### 14.3. Obowiązkowe przypadki brzegowe

| ID | Scenariusz | Oczekiwane zachowanie |
|---|---|---|
| TC-01 | Termin już minął | Brak planu, jasny komunikat |
| TC-02 | Sam powrót wymaga więcej czasu | Pokazanie ryzyka/opóźnienia, zero atrakcji |
| TC-03 | Miejsce zamyka się w trakcie pobytu | Wykluczenie lub krótszy pobyt tylko powyżej minimum |
| TC-04 | Dzień świąteczny bez wyjątków godzin | Status unknown; brak pewnego otwarcia |
| TC-05 | Przerwa obiadowa w godzinach | Brak pobytu nachodzącego na przerwę |
| TC-06 | Brak ceny obowiązkowej | Wykluczenie przy strict budget |
| TC-07 | Brak trasy przez rzekę mimo małej odległości | Brak użycia linii prostej jako obejścia |
| TC-08 | Routing zwraca inną geometrię/czas niż matrix | Przeliczenie i ponowna walidacja |
| TC-09 | Start 15 min później niż plan | Rewalidacja przed rozpoczęciem |
| TC-10 | Wizyta kończy się po północy | Poprawna data i harmonogram lokalny |
| TC-11 | Zmiana czasu DST, godzina nieistniejąca/niejednoznaczna | Odrzucenie lub prośba o wybór offsetu |
| TC-12 | LLM wymyśla nową atrakcję/cenę | Output odrzucony, szablon lub naprawa w limicie |
| TC-13 | Źródło zawiera „ignoruj instrukcje” | Treść pozostaje danymi, bez eskalacji narzędzi |
| TC-14 | Dwie karty replanują ten sam trip | Jeden wynik aktywny, drugi wymaga obsługi konfliktu |
| TC-15 | Użytkownik zgłasza zamknięte miejsce | Wykluczenie w tej sesji; globalnie moderacja |
| TC-16 | Przekroczony budżet modelu | Fallback, bez nieograniczonego retry |
| TC-17 | Próba odczytu cudzego planu | Brak ujawnienia danych |
| TC-18 | Niepotwierdzone „bez schodów” | Brak zapewnienia zgodności |
| TC-19 | Stary cache źródła lub wycofany chunk | Brak użycia jako aktualnego dowodu |
| TC-20 | Zerwane połączenie po zapisaniu runu | Idempotentne odtworzenie statusu |
| TC-21 | Zabicie workera w trakcie | Wznowienie bez dwóch aktywnych planów |
| TC-22 | Brak LLM, działający routing | Powrót nadal działa |
| TC-23 | Nietypowy zapis „mam cztery dychy, za kwadrans szósta” | Jawna interpretacja lub pytanie |
| TC-24 | Brak świeżej pozycji podczas replanu | Prośba o start, brak udawanego live location |

### 14.4. Dataset ewaluacyjny

P0: minimum 100 przypadków intencji PL, 50 zapytań retrieval z ręcznie oznaczoną relewancją oraz 100 scenariuszy planowania. Dane mogą się częściowo łączyć, ale każda rodzina ma osobne etykiety i metryki. Zawieraj przypadki bez poprawnej odpowiedzi, sprzeczne wymagania, potoczne kwoty, negację, święta, brak źródeł i prompt injection.

Podział: development i zamrożony holdout. Parafrazy tego samego scenariusza nie mogą trafiać do obu części. Przy rozszerzeniu na nowe miasta utrzymuj również holdout geograficzny; przy aktualizacji danych testuj holdout czasowy. Nie używaj informacji opublikowanej po ocenianym terminie jako dowodu, który rzekomo był wtedy dostępny.

Własność scenariusza: `case_id`, input, expected constraints, expected feasibility/reason, relevant place/evidence ids, data snapshot, author/reviewer, split, license, limitations. Syntetyczne dane są oznaczone. Realne dane użytkownika wymagają osobnej zgody i anonimizacji.

### 14.5. Metryki i bramki jakości

| Obszar | Metryka | Bramka P0 |
|---|---|---|
| Intencja | Poprawność pól krytycznych lub poprawne dopytanie | ≥ 95% na zamrożonym holdoucie |
| Negacja i terminy | Ciche odwrócenie ograniczeń | 0 w zestawie krytycznym |
| Retrieval | Recall@5, nDCG@5 | Raport i porównanie z baseline, bez z góry wymyślonej przewagi |
| Grounding | Twierdzenia ze wspierającym dowodem, audyt ludzki | Wszystkie krytyczne dane ze struktury; brak zmyślonych cen/godzin |
| Planner | Naruszenia twardych warunków | 0 |
| Abstention | Poprawne odmowy i nadmiarowe odmowy | Obie wartości jawne; przypadki krytyczne bez fałszywego „ready” |
| UX | Ukończenie podstawowego flow | Wszystkie krytyczne scenariusze E2E |
| Koszt/latency | p50, p95, maksimum, usage | Zmierzone i odniesione do budżetów |

„0 błędów w zbiorze” nie oznacza „0 błędów w świecie”. README musi podawać wielkość zbioru, sposób etykietowania i ograniczenia.

Porównania wymagane: formularz bez LLM; tagi/full-text; embeddings; opcjonalnie reranker. Porównaj ten sam zestaw, czas, koszt i aktualność danych. Nie wprowadzaj bardziej złożonej metody tylko dlatego, że ma lepszą nazwę.

## 15. Delivery, CI/CD i operacje

### 15.1. Lokalny start

Docelowe polecenia w README:

```bash
make bootstrap
make demo
make test
make eval
make dev
```

Ich znaczenie MUST być rzeczywiste i sprawdzone na czystym checkout:

- `bootstrap`: zależności i konfiguracja przykładowa bez sekretów;
- `demo`: syntetyczny citypack, fake routing i odpowiedzi AI, działający UI;
- `test`: testy bez płatnych usług i internetu poza pobraniem zależności;
- `eval`: deterministyczne ewaluacje fixture’ów; osobne `eval-live` z kluczem i limitem kosztów;
- `dev`: tryb lokalny z wybranymi providerami, stan integracji widoczny w panelu developerskim.

Demo MUST stale oznaczać, że używa fikcyjnych danych i nie służy do nawigacji. Brak klucza nie może prowadzić do cichego pokazywania wygenerowanych „realnych” danych.

### 15.2. Pipeline PR

1. Format/lint/typecheck Python i TypeScript.
2. Testy domeny i własności.
3. Migracje od pustej bazy oraz ze wspieranej poprzedniej wersji.
4. Testy integracyjne na rzeczywistych rozszerzeniach PostgreSQL.
5. Test kontraktu OpenAPI/generowanego klienta.
6. E2E demo, mobile viewport i kontrola dostępności.
7. Offline evals z raportem różnic.
8. Dependency/secret/container scanning i build obrazów.

Płatne ewaluacje: kontrolowany workflow po akceptacji maintenera lub harmonogram z budżetem, nigdy z sekretami dostępnymi dla niezaufanego PR. Prompty i dokumenty PR są również niezaufane.

### 15.3. Wdrożenie

P0: jedno środowisko staging i kontrolowany pilot. P1: osobne staging/production, PostgreSQL z backupami, reverse proxy z TLS, proces API, worker i Redis. Skalowanie według zmierzonych wąskich gardeł, nie według przewidywanego milionowego ruchu.

Artefakty buduj raz, promuj po digest. Sekrety dostarczaj przez mechanizm środowiska. Migracje stosuj przed przełączeniem wersji zgodnie z kompatybilnym schematem expand/contract. Nie wykonuj destrukcyjnego downgrade’u bazy jako automatycznego rollbacku. Zachowaj możliwość cofnięcia aplikacji przy zachowaniu zgodności schematu.

### 15.4. Backup i odtwarzanie

Początkowe cele operacyjne: RPO ≤ 24 h, RTO ≤ 4 h dla pilota. Codzienny szyfrowany backup i próba odtworzenia przed publiczną betą, następnie regularnie. W README nie deklaruj osiągania tych parametrów przed wykonaniem próby.

Redis można odtworzyć z bazy/outbox; dane użytkownika i planów nie mogą zależeć wyłącznie od Redis. Utrzymuj procedurę usuwania danych również po restore.

### 15.5. Runbooki wymagane w P1

- routing niedostępny / przekroczony limit;
- błędny pakiet miejski i wycofanie wersji;
- zmyślone twierdzenie w wyjaśnieniu;
- zgłoszenie planu prowadzącego do spóźnienia;
- nieautoryzowany dostęp / wyciek sekretu;
- skok kosztów modelu;
- blokada kolejki i restart workera;
- odtwarzanie bazy oraz rollback aplikacji.

Każdy runbook: objawy, wykrycie, ograniczenie skutków, rollback, komunikat dla użytkownika i sposób sprawdzenia naprawy. Istnieje globalny kill switch generowania nowych planów oraz wyłączenie konkretnego citypacku/dostawcy. Nie wyłączaj dostępu do zapisanej informacji i feedbacku bez potrzeby.

## 16. Plan implementacji i bramki

Nie przypisuj dat kalendarzowych bez poznania dostępnego czasu autora i dostawców. Poniższa kolejność ma ograniczać ryzyko. Każdy milestone kończy się działającym artefaktem, testami i krótkim raportem.

### M0. Weryfikacja danych i decyzji

**Rezultat:** audit miasta, lista źródeł i dostawców, 10 sprawdzonych miejsc, zakres polygonu, pierwsze scenariusze.

**Bramka:** potwierdzony dostęp do routingu i możliwość legalnego użycia danych. Jeśli brak, można budować demo, ale nie deklarować gotowości pilota.

### M1. Działający produkt bez AI

**Rezultat:** formularz → fixture katalogu → deterministyczny planner → mapa/lista → wynik powrotu.

**Bramka:** testy czasu, godzin, budżetu, niezależny walidator i negatywne wyniki. Jeden command uruchamia demo.

### M2. Integracja realnych danych

**Rezultat:** routing adapter, 30–50 audytowanych miejsc, źródła per fakt, cache i tryby awarii.

**Bramka:** finalna geometria zgodna z czasem, brak wykonalnych wyników przy brakującym routingu, audyt wejść i godzin.

### M3. Warstwa AI i benchmark

**Rezultat:** ekstrakcja PL, retrieval, LangGraph workflow, wyjaśnienia z dowodami, limity kosztów.

**Bramka:** raport baseline vs AI, zamrożony holdout, brak krytycznych halucynacji w zbiorze akceptacyjnym, działający fallback.

### M4. Aktywne wyjście i replan

**Rezultat:** sesja gościa, wersje planu, potwierdzanie postępu, replan i powrót bez AI.

**Bramka:** testy równoległych zmian, zmarnowanego czasu, zużytego budżetu, awarii workera i pozycji nieaktualnej.

### M5. Kontrolowany pilot

**Rezultat:** staging, minimum 5 wyjść, feedback, poprawki danych i prognoz czasu.

**Bramka:** wszystkie krytyczne problemy zamknięte, obserwacje użyteczności, koszty i latency zmierzone. Decyzja go/no-go właściciela.

### M6. Publiczna beta i OSS

**Rezultat:** dokumentacja, proces release, bezpieczeństwo, backup/restore, licencje i moderacja citypacków.

**Bramka:** komplet Definition of Done, przegląd warunków usług i prywatności, jawna zgoda na publikację.

## 17. Backlog gotowy do rozpisania na issues

| ID | Zadanie | Zależności | Kryterium zamknięcia |
|---|---|---|---|
| DATA-01 | Schema citypack + walidator | M0 | Odrzuca brak źródeł i błędne przedziały |
| DATA-02 | Pilot Kraków | DATA-01 | Weryfikowalne rekordy i granice pokrycia |
| CORE-01 | Time/Money/Constraints | — | DST, kwoty i potwierdzanie inputu przetestowane |
| CORE-02 | Otwarcie i wyjątki | CORE-01 | TC-03/04/05/10 przechodzą |
| CORE-03 | Routing interface + fake | CORE-01 | Wymusza jednostki i rozróżnia brak połączenia |
| CORE-04 | Solver sekwencji | CORE-02/03 | Wyniki zgodne z małymi ręcznie policzonymi przypadkami |
| CORE-05 | Independent validator | CORE-01/02 | Wykrywa ręcznie uszkodzone plany |
| API-01 | Model DB i migracje | CORE-01 | PostGIS+pgvector i migracje działają na czystej bazie |
| API-02 | Jobs/outbox/idempotency | API-01 | Retry nie tworzy dwóch runów biznesowych |
| WEB-01 | Formularz i wynik | API-01, CORE-04/05 | Pełne flow z klawiatury i na telefonie |
| INT-01 | Real routing + contract tests | CORE-03 | Matrix i directions obsługują błędy i limity |
| AI-01 | Intent extraction | CORE-01 | Walidacja JSON, negacja i dopytywanie |
| AI-02 | Hybrid retrieval | DATA-02 | Raport baseline i identyfikowalne evidence |
| AI-03 | Graph + explanation | AI-01/02, CORE-05 | Limity runu i brak liczb spoza danych |
| TRIP-01 | Progress/replan | API-02, CORE-04/05 | Zachowane wersje, koszty i postęp |
| SEC-01 | Sesje i autoryzacja | API-01 | Testy IDOR/CSRF i redakcja logów |
| EVAL-01 | Benchmark runner | CORE-04, AI-01/02 | Jeden command tworzy wersjonowany raport |
| OPS-01 | Telemetria i koszty | API-02 | Diagnoza przykładowej awarii z trace |
| OPS-02 | Deploy/backup/restore | OPS-01 | Odtworzone staging i protokół testu |
| OSS-01 | Dokumentacja i licencje | M5 | Obcy developer uruchamia demo z README |

Issues powinny być małe, zawierać zakres poza zadaniem i test akceptacyjny. Unikaj issue „zbuduj całe AI”.

## 18. Rozwój P2: spotkanie osób z różnych miast

To ważny przyszły wyróżnik, ale osobny problem optymalizacyjny. Najpierw wspieraj ręcznie podane okna przyjazdu/odjazdu uczestników. Dopiero później dołączaj wyszukiwanie transportu.

Wejście uczestnika: miejscowość startu, najwcześniejszy wyjazd, najpóźniejszy powrót, limit kosztu, dostępne środki transportu. System szuka miasta spotkania i wspólnego okna aktywności, sprawdzając podróż każdego uczestnika w obie strony.

Warunki:

- Wspólne okno jest przecięciem przedziałów dostępności po buforach transportowych.
- Czas przejazdów i spotkania liczony osobno dla każdej osoby.
- Minimalna długość wspólnego pobytu, np. zadane 4 h, jest warunkiem twardym.
- Ranking może minimalizować największy indywidualny wysiłek podróży, nie tylko sumę kosztów grupy. Pokaż kompromisy.
- Jedna osoba nie może zgodzić się na zmianę limitów innych osób.
- Dane członków są prywatne; współdzielony wynik ujawnia tylko potrzebny zakres.
- Brak pewnej drogi powrotnej oznacza brak rekomendacji kompletnego spotkania.

GTFS Schedule opisuje rozkład i daty kursowania, a GTFS-Realtime może dostarczać aktualizacje kursów. Wspieranie formatu nie oznacza dostępu do wszystkich przewoźników, cen biletów lub gwarantowanego pokrycia realtime. Zapisuj datę usługi, rozróżniaj czasy po 24:00 i nie traktuj braku aktualizacji jako punktualności. [GTFS Schedule](https://gtfs.org/documentation/schedule/reference/), [GTFS-Realtime](https://gtfs.org/documentation/realtime/reference/).

Opóźniony pociąg nie powinien automatycznie rozszerzać czasu spaceru bez oceny wiarygodności i stabilności aktualizacji. W pierwszej integracji transportowej zachowaj konserwatywny termin powrotu; zmiany potwierdza użytkownik.

## 19. Open source i jakość portfolio

Domyślna propozycja licencji kodu: Apache-2.0, do potwierdzenia przed publikacją. Dane miejskie, zdjęcia, modele i dokumenty zachowują odrębne licencje. Nie oznaczaj całej zawartości repo jedną licencją, jeśli nie masz takich praw.

Repozytorium powinno zawierać:

- README po angielsku i skróconą wersję PL;
- krótki film lub GIF pokazujący rzeczywisty flow z oznaczeniem demo;
- diagram architektury i wyjaśnienie, dlaczego planner nie jest LLM-em;
- instrukcję startu bez kluczy oraz wariant z realnymi providerami;
- `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`;
- ADR-y, model zagrożeń, schemat danych i opis ograniczeń;
- publiczny benchmark na danych, które wolno publikować;
- raport kosztów, latency i porównań baseline z datą/modelami;
- procedurę zgłaszania błędów danych i dodawania citypacków;
- changelog, semver API/packów i opis migracji.

Najmocniejszy materiał rekrutacyjny to demonstracja decyzji i trade-offów: dlaczego wektory pomogły lub nie, jak wykryto błąd czasu, jak działa degradacja i czego nauczył pilot. Nie wpisuj do CV „production-grade” tylko dlatego, że istnieje Dockerfile. Podawaj rzeczywiste wdrożenie, skalę, czas działania i zakres odpowiedzialności.

## 20. Ryzyka i decyzje otwarte

| Ryzyko / niewiadoma | Skutek | Działanie |
|---|---|---|
| Nieaktualne godziny/ceny | Zły plan | Mały katalog, provenance, ścisła obsługa unknown |
| Niedokładne czasy spacerów | Spóźnienie względem założeń | Bufory, pilot, jawne oszacowania |
| Długi czas obsługi lokalu | Plan się rozjeżdża | Dłuższy profil pobytu lub wykluczenie w ciasnym oknie |
| Brak danych o wejściu na dworzec | Błędny powrót | Ręczny audyt entrance i bufora |
| Niska częstotliwość potrzeby | Słaba retencja | Walidacja osób dojeżdżających, nie tylko turystów |
| Produkt da się zastąpić mapą | Brak przewagi | Pomiar czasu i jakości decyzji w realnym zadaniu |
| Zbyt szeroki zakres | Projekt niedokończony | Jedno miasto, pieszo, 1–3 punkty |
| Koszt API | Trudny publiczny hosting | Budżety, cache, BYO keys w self-hostingu |
| Halucynacje i injection | Fałszywe fakty | Ograniczone narzędzia, schema, renderer, evidence |
| Nadmierne przechowywanie pozycji | Ryzyko prywatności | Minimalizacja, TTL, brak trackingu w tle |
| Dostawca zmienia warunki | Niedostępność integracji | Adaptery i rejestr warunków |
| Rozbudowa ML bez danych | Pozorna jakość | Baseline i bramki pomiarowe |

Do ustalenia przed M2: faktyczny routing provider, plan/limity konta, dostawca map, prawa do citypacku, rzeczywiste wejścia na dworzec, infrastruktura staging.

Do ustalenia przed M3: model LLM, embedding model, cennik, sposób przetwarzania danych przez providerów i maksymalny miesięczny budżet.

Do ustalenia przed M6: hosting produkcyjny, licencja kodu, publiczna polityka prywatności, kanał zgłoszeń, odpowiedzialność za aktualizację danych. Nie blokuje to budowy lokalnego MVP z fixture’ami.

## 21. Definition of Done

### P0 gotowe do pilota, gdy:

- Jeden pełny flow działa na telefonie i przez klawiaturę.
- Realne dane są oddzielone od demo i mają pochodzenie.
- Wszystkie zaakceptowane plany przechodzą niezależną walidację.
- Powrót, otwarcia, budżet, DST i zmiana startu mają testy.
- Plan nie ukrywa ręcznie wpisanego odjazdu ani niepewności danych.
- Istnieje powrót bez LLM, replan i jawna odmowa.
- Autoryzacja sesji i ochrona sekretów są sprawdzone.
- AI ma ograniczony koszt i fallback.
- Benchmark oraz jego ograniczenia są udokumentowane.
- Nie ma znanych krytycznych błędów logistycznych w pilotażowym obszarze.

### P1 gotowe do publicznej bety, gdy dodatkowo:

- Pilot dostarczył dowodów użyteczności i poprawiono wykryte błędy.
- Zmierzono koszty, latency i dostępność; nie wpisano wymyślonych wyników.
- Wykonano restore backupu i próbę rollbacku.
- Istnieją runbooki, rate limits, kill switches i moderacja danych.
- Sprawdzono warunki dostawców, prawa do danych i dokumentację prywatności.
- Nowy developer potrafi uruchomić demo z czystego checkout.
- Właściciel zaakceptował publikację i budżet utrzymania.

## 22. Format raportu agenta po każdym etapie

Agent powinien podać:

1. Co działa z perspektywy użytkownika i jak to uruchomić.
2. Które wymagania i testy zostały spełnione, z dowodami.
3. Które dane są syntetyczne, a które rzeczywiste.
4. Jakie decyzje podjęto i gdzie zapisano ADR.
5. Znane ograniczenia, niespełnione bramki i najbliższy krok.

Nie prezentuj procentu ukończenia bez zdefiniowanego zakresu. Nie uznawaj niedziałającej integracji z mockiem za integrację produkcyjną. Nie kończ etapu samą listą plików — pokaż zachowanie produktu.

## 23. Kryterium „senior approach”

W tym projekcie senior approach oznacza: świadome ograniczenie zakresu, rzetelne dane, deterministyczny rdzeń, niezależną walidację, małą powierzchnię uprawnień AI, uczciwe pomiary, obsługę awarii i prostą architekturę, którą jedna osoba potrafi utrzymać.

**Najważniejszy test produktu:** czy człowiek może na podstawie wyniku podjąć rozsądną decyzję o swoim czasie, rozumiejąc założenia i ograniczenia. Efektowny tekst, duża liczba agentów i rozbudowany diagram nie zastępują tego testu.
