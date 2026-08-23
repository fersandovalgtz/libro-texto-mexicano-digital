# LTMD-U1 — configuración de representaciones oficiales candidatas

Versión: `LTMD_U1_OFFICIAL_REPRESENTATION_CONFIG_0.1`.

Se extraen metadatos de configuración desde JavaScript oficial de CONALITEG y se contrastan con los manifiestos W11 ya publicados. No se declara equivalencia documental ni se persisten imágenes.

## `H2014P3COL` / `P3COL`

- Configuración oficial: `https://libros.conaliteg.gob.mx/2022/x.js`.
- SHA-256 del JS: `ba93f5bfa61541bfc54271b7b8eb21bb0d54d690fa6ffcfb82000005f3a1209a`.
- Filas históricas W11 localizadas: **161**.
- Manifiestos: `ltmd_u1_w11_standard_asset_manifest.csv`.
- Rango de índices históricos observado: **0–161**.
- Asignaciones técnicas relevantes: **0**.
- Strings de ruta/configuración detectados: **16**.

Patrones/string de arquitectura:
- `#ag_page`
- `));
		ag_pages = data[clavesUrl.at(0)][ag_clave].ag_pages;
		loadApp();
	})
	.catch(error => console.error(`
- `),
					pages = book.turn(`
- `).fadeIn(1000);

 	var flipbook = $(`
- `).zoom({
		flipbook: $(`
- `);
					}

				},

				missing: function (event, pages) {

					// Add pages that aren`
- `);
		return response.json()
	})
	.then(data => {
		console.log(data);
		clave = clavesUrl.at(1);
		ag_clave = clave.substring(0, clave.indexOf(`
- `);

					if (page==1) { 
						$(this).turn(`
- `);

			},

			resize: function(event, scale, page, pageElement) {

				if (scale==1)
					loadSmallPage(page, pageElement);
				else
					loadLargePage(page, pageElement);

			},

			zoomIn: function () {

				$(`
- `);



				},

				turned: function(event, page, view) {

					disableControls(page);

					$(this).turn(`
- `);

 	// Check if the CSS was already loaded
	
	if (flipbook.width()==0 || flipbook.height()==0) {
		setTimeout(loadApp, 10);
		return;
	}
	

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
// crea el libro
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 


	flipbook.turn({
			
			// Magazine width

			width: 922,

			// Magazine height

			height: 600,

			// Duration in millisecond

			duration: 1000,

			// Hardware acceleration

			acceleration: !isChrome(),

			// Enables gradients

			gradients: true,
			
			// Auto center this flipbook

			autoCenter: true,

			// Elevation from the edge of the flipbook when turning a page

			elevation: 50,

			// The number of pages

			pages: ag_pages,

			// Events

			when: {
				turning: function(event, page, view) {
					
					var book = $(this),
					currentPage = book.turn(`
- `.thumbnails .page-`
- `^page\/([0-9]*)$`
- `flipbook`
- `page`
- `page/`

Estados históricos observados:
- `internal_unserved`: **1**.
- `source_jpeg`: **160**.

## `H2014P3MOR` / `P3MOR`

- Configuración oficial: `https://libros.conaliteg.gob.mx/x.js`.
- SHA-256 del JS: `ff795d0aa986540eec669fea57146db26b0da8f8d7043a9d8538700a498ddad2`.
- Filas históricas W11 localizadas: **161**.
- Manifiestos: `ltmd_u1_w11_standard_asset_manifest.csv`.
- Rango de índices históricos observado: **0–161**.
- Asignaciones técnicas relevantes: **0**.
- Strings de ruta/configuración detectados: **14**.

Patrones/string de arquitectura:
- `#ag_page`
- `),
					pages = book.turn(`
- `).fadeIn(1000);

 	var flipbook = $(`
- `).zoom({
		flipbook: $(`
- `);
					}

				},

				missing: function (event, pages) {

					// Add pages that aren`
- `);

					if (page==1) { 
						$(this).turn(`
- `);

			},

			resize: function(event, scale, page, pageElement) {

				if (scale==1)
					loadSmallPage(page, pageElement);
				else
					loadLargePage(page, pageElement);

			},

			zoomIn: function () {

				$(`
- `);



				},

				turned: function(event, page, view) {

					disableControls(page);

					$(this).turn(`
- `);

 	// Check if the CSS was already loaded
	
	if (flipbook.width()==0 || flipbook.height()==0) {
		setTimeout(loadApp, 10);
		return;
	}
	

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 
// crea el libro
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * 


	flipbook.turn({
			
			// Magazine width

			width: 922,

			// Magazine height

			height: 600,

			// Duration in millisecond

			duration: 1000,

			// Hardware acceleration

			acceleration: !isChrome(),

			// Enables gradients

			gradients: true,
			
			// Auto center this flipbook

			autoCenter: true,

			// Elevation from the edge of the flipbook when turning a page

			elevation: 50,

			// The number of pages

			pages: ag_pages,

			// Events

			when: {
				turning: function(event, page, view) {
					
					var book = $(this),
					currentPage = book.turn(`
- `.thumbnails .page-`
- `^page\/([0-9]*)$`
- `flipbook`
- `page`
- `page/`

Estados históricos observados:
- `internal_unserved`: **1**.
- `source_jpeg`: **160**.

## Criterio para la siguiente compuerta

Sólo si la configuración oficial permite construir una secuencia de activos con cardinalidad compatible se habilitará una comparación criptográfica temporal. Esa comparación deberá demostrar correspondencia posicional en todas las posiciones históricas servidas; una coincidencia parcial o nominal no recupera el hueco.
