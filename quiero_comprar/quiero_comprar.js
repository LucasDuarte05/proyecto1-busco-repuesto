// Datos de modelos por marca
const modelosPorMarca = {
    'Chevrolet': ['Agile', 'Astra', 'Aveo', 'Blazer', 'Captiva', 'Classic', 'Cobalt', 'Corsa', 'Cruze', 'Montana', 'Onix', 'Prisma', 'S10', 'Sail', 'Sonic', 'Spark', 'Spin', 'Tracker', 'Trailblazer', 'Zafira'],
    'Ford': ['EcoSport', 'Edge', 'Escort', 'Explorer', 'F-100', 'F-150', 'Fiesta', 'Focus', 'Fusion', 'Ka', 'Kuga', 'Mondeo', 'Mustang', 'Ranger', 'Territory', 'Transit'],
    'Volkswagen': ['Amarok', 'Beetle', 'Bora', 'Caddy', 'Fox', 'Gol', 'Golf', 'Jetta', 'Passat', 'Polo', 'Saveiro', 'Suran', 'T-Cross', 'Tiguan', 'Touareg', 'Up', 'Vento', 'Virtus'],
    'Fiat': ['500', 'Argo', 'Bravo', 'Cronos', 'Doblo', 'Ducato', 'Fiorino', 'Idea', 'Linea', 'Mobi', 'Palio', 'Punto', 'Siena', 'Strada', 'Toro', 'Uno', 'Weekend'],
    'Peugeot': ['106', '205', '206', '207', '208', '2008', '301', '307', '308', '3008', '405', '406', '407', '408', '5008', '504', '505', 'Partner', 'Boxer'],
    'Renault': ['Alaskan', 'Captur', 'Clio', 'Duster', 'Fluence', 'Kangoo', 'Koleos', 'Kwid', 'Logan', 'Master', 'Megane', 'Oroch', 'Sandero', 'Scenic', 'Stepway', 'Symbol', 'Talisman', 'Twingo'],
    'Toyota': ['Camry', 'Corolla', 'Etios', 'Hilux', 'Land Cruiser', 'Prius', 'RAV4', 'SW4', 'Yaris'],
    'Honda': ['Accord', 'City', 'Civic', 'CR-V', 'Fit', 'HR-V', 'Pilot'],
    'Nissan': ['Frontier', 'Kicks', 'March', 'Murano', 'Pathfinder', 'Sentra', 'Tiida', 'Versa', 'X-Trail'],
    'Citroen': ['C3', 'C4', 'C4 Cactus', 'C4 Lounge', 'C5', 'Berlingo', 'Jumper'],
    'Hyundai': ['Accent', 'Creta', 'Elantra', 'i10', 'i30', 'Ioniq', 'Kona', 'Santa Fe', 'Tucson', 'Veloster'],
    'Kia': ['Carnival', 'Cerato', 'Picanto', 'Rio', 'Seltos', 'Sorento', 'Sportage', 'Soul'],
    'Mazda': ['2', '3', '6', 'CX-3', 'CX-5', 'CX-9'],
    'Mitsubishi': ['ASX', 'Eclipse', 'L200', 'Lancer', 'Montero', 'Outlander', 'Pajero'],
    'Suzuki': ['Alto', 'Baleno', 'Celerio', 'Fun', 'Grand Vitara', 'Swift', 'Vitara']
};

// Repuestos por categoría
const repuestosPorCategoria = {
    'motor': ['Alternador', 'Motor de arranque', 'Bomba de agua', 'Bomba de aceite', 'Filtro de aceite', 'Filtro de aire', 'Bujías', 'Cables de bujía', 'Correa de distribución', 'Tensor de correa', 'Radiador', 'Termostato', 'Junta de tapa', 'Sensor de temperatura'],
    'transmision': ['Embrague completo', 'Disco de embrague', 'Plato de embrague', 'Crapodina', 'Caja de cambios', 'Semieje', 'Cruceta', 'Fuelle de transmisión'],
    'suspension': ['Amortiguador delantero', 'Amortiguador trasero', 'Espiral delantero', 'Espiral trasero', 'Brazo de suspensión', 'Rótula', 'Barra estabilizadora', 'Bujes de suspensión', 'Tren delantero'],
    'frenos': ['Disco de freno delantero', 'Disco de freno trasero', 'Pastillas de freno', 'Zapatas de freno', 'Bomba de freno', 'Cilindro de freno', 'Manguera de freno', 'Líquido de freno'],
    'electrico': ['Batería', 'Alternador', 'Motor de arranque', 'Bobina de encendido', 'Módulo de encendido', 'Sensor de oxígeno', 'Sensor MAF', 'Computadora de motor', 'Arnés eléctrico', 'Fusibles', 'Relés'],
    'carroceria': ['Óptica delantera', 'Óptica trasera', 'Paragolpes delantero', 'Paragolpes trasero', 'Guardabarro', 'Capot', 'Puerta', 'Espejo retrovisor', 'Luneta', 'Parabrisas'],
    'interior': ['Tablero', 'Volante', 'Asientos', 'Tapizado', 'Alfombras', 'Consola central', 'Palanca de cambios', 'Manijas', 'Vidrio eléctrico', 'Cerradura'],
    'otros': ['Neumáticos', 'Llantas', 'Tapa de tanque', 'Antena', 'Escape', 'Silenciador', 'Catalizador', 'Limpia parabrisas', 'Otros repuestos']
};

// Datos de provincias y localidades de Argentina
const localidadesPorProvincia = {
    'Buenos Aires': ['La Plata', 'Mar del Plata', 'Bahía Blanca', 'Quilmes', 'Avellaneda', 'Lanús', 'San Isidro', 'Lomas de Zamora', 'Morón', 'San Miguel', 'Tigre', 'Vicente López', 'Tres de Febrero', 'La Matanza', 'Almirante Brown', 'Pilar', 'Escobar', 'General San Martín', 'Tandil', 'Olavarría', 'Pergamino', 'Junín', 'Necochea', 'Zárate', 'Campana', 'San Nicolás', 'Luján', 'Mercedes', 'Chivilcoy', 'San Pedro', 'Azul', 'Balcarce', 'Bragado', 'Chascomús', 'Dolores', 'General Pueyrredón', 'La Costa', 'Pinamar', 'Villa Gesell'],
    'CABA': ['Palermo', 'Recoleta', 'Belgrano', 'Caballito', 'Almagro', 'Villa Urquiza', 'Flores', 'Villa Crespo', 'San Telmo', 'Puerto Madero', 'Núñez', 'Colegiales', 'Villa Devoto', 'Villa del Parque', 'Paternal', 'Chacarita', 'Agronomía', 'Saavedra', 'Coghlan', 'Villa Ortúzar', 'Parque Chas', 'Villa Pueyrredón', 'Monte Castro', 'Versalles', 'Liniers', 'Mataderos', 'Parque Avellaneda', 'Floresta', 'Vélez Sarsfield', 'Villa Luro', 'Villa Real', 'Parque Chacabuco', 'Boedo', 'Barracas', 'La Boca', 'Constitución', 'San Cristóbal', 'Balvanera', 'Once', 'Retiro', 'San Nicolás', 'Monserrat'],
    'Catamarca': ['San Fernando del Valle de Catamarca', 'Andalgalá', 'Belén', 'Santa María', 'Tinogasta', 'Fiambalá', 'Valle Viejo', 'Recreo', 'Fray Mamerto Esquiú', 'Capayán', 'Pomán', 'Ancasti'],
    'Chaco': ['Resistencia', 'Barranqueras', 'Fontana', 'Puerto Vilelas', 'Sáenz Peña', 'Villa Ángela', 'Charata', 'General San Martín', 'Quitilipi', 'Las Breñas', 'Machagai', 'Castelli', 'Juan José Castelli'],
    'Chubut': ['Rawson', 'Puerto Madryn', 'Comodoro Rivadavia', 'Trelew', 'Esquel', 'Puerto Deseado', 'Rada Tilly', 'Gaiman', 'Dolavon', 'Trevelin', 'Sarmiento', 'Gobernador Costa', 'Río Mayo'],
    'Córdoba': ['Córdoba', 'Villa Carlos Paz', 'Río Cuarto', 'Villa María', 'San Francisco', 'Alta Gracia', 'Río Tercero', 'Bell Ville', 'Jesús María', 'La Calera', 'Cosquín', 'Cruz del Eje', 'Villa Dolores', 'Deán Funes', 'La Falda', 'Arroyito', 'San Francisco del Chañar', 'Laboulaye', 'Villa Allende', 'Unquillo', 'Río Segundo', 'Villa del Rosario', 'Morteros', 'Marcos Juárez', 'Las Varillas', 'Corral de Bustos', 'Villa Nueva', 'Villa General Belgrano'],
    'Corrientes': ['Corrientes', 'Goya', 'Mercedes', 'Paso de los Libres', 'Curuzú Cuatiá', 'Santo Tomé', 'Esquina', 'Monte Caseros', 'Bella Vista', 'Saladas', 'Ituzaingó', 'Alvear'],
    'Entre Ríos': ['Paraná', 'Concordia', 'Gualeguaychú', 'Concepción del Uruguay', 'Gualeguay', 'La Paz', 'Federación', 'Victoria', 'Villaguay', 'Colón', 'San José', 'Chajarí', 'Federal', 'Basavilbaso', 'Crespo', 'San Salvador', 'Diamante', 'Nogoyá'],
    'Formosa': ['Formosa', 'Clorinda', 'Pirané', 'El Colorado', 'Ingeniero Juárez', 'Las Lomitas', 'Laguna Blanca', 'Comandante Fontana', 'Ibarreta', 'Misión Laishí', 'Villa Escolar', 'Herradura'],
    'Jujuy': ['San Salvador de Jujuy', 'San Pedro', 'Libertador General San Martín', 'Palpalá', 'La Quiaca', 'Humahuaca', 'Perico', 'El Carmen', 'Tilcara', 'Monterrico', 'Libertad', 'Fraile Pintado', 'Yuto'],
    'La Pampa': ['Santa Rosa', 'General Pico', 'General Acha', 'Toay', 'Eduardo Castex', 'Realicó', 'Intendente Alvear', 'Macachín', 'Victorica', 'Winifreda', 'Ingeniero Luiggi', 'Quemú Quemú'],
    'La Rioja': ['La Rioja', 'Chilecito', 'Arauco', 'Chamical', 'Aimogasta', 'Villa Unión', 'Chepes', 'Nonogasta', 'Famatina', 'Vinchina'],
    'Mendoza': ['Mendoza', 'San Rafael', 'Godoy Cruz', 'Guaymallén', 'Luján de Cuyo', 'Maipú', 'Las Heras', 'San Martín', 'Rivadavia', 'Junín', 'Tunuyán', 'Tupungato', 'Malargüe', 'General Alvear', 'Lavalle', 'La Paz', 'Santa Rosa', 'San Carlos'],
    'Misiones': ['Posadas', 'Oberá', 'Eldorado', 'Puerto Iguazú', 'Apóstoles', 'Leandro N. Alem', 'San Vicente', 'Montecarlo', 'Jardín América', 'Puerto Rico', 'Aristóbulo del Valle', 'Wanda', 'Campo Grande', 'Garupá', 'Candelaria', 'San Ignacio'],
    'Neuquén': ['Neuquén', 'Plottier', 'Centenario', 'Cutral-Có', 'Plaza Huincul', 'Zapala', 'San Martín de los Andes', 'Junín de los Andes', 'Villa La Angostura', 'Chos Malal', 'Senillosa', 'San Patricio del Chañar', 'Añelo', 'Loncopué', 'Aluminé'],
    'Río Negro': ['Viedma', 'San Carlos de Bariloche', 'General Roca', 'Cipolletti', 'Villa Regina', 'Río Colorado', 'Allen', 'Cinco Saltos', 'Catriel', 'El Bolsón', 'Choele Choel', 'San Antonio Oeste', 'Las Grutas', 'Ingeniero Jacobacci', 'Sierra Grande'],
    'Salta': ['Salta', 'San Ramón de la Nueva Orán', 'Tartagal', 'Metán', 'General Güemes', 'Cafayate', 'Joaquín V. González', 'Rosario de la Frontera', 'Embarcación', 'Cerrillos', 'Chicoana', 'La Caldera', 'El Carril', 'Campo Quijano', 'Cachi', 'Molinos'],
    'San Juan': ['San Juan', 'Rawson', 'Chimbas', 'Rivadavia', 'Santa Lucía', 'Pocito', 'Caucete', 'Albardón', '9 de Julio', '25 de Mayo', 'Jáchal', 'Valle Fértil', 'Calingasta', 'Iglesia'],
    'San Luis': ['San Luis', 'Villa Mercedes', 'La Punta', 'Merlo', 'Juana Koslay', 'El Trapiche', 'Tilisarao', 'Naschel', 'Justo Daract', 'Villa de la Quebrada', 'Concarán', 'La Toma', 'Quines', 'San Francisco del Monte de Oro'],
    'Santa Cruz': ['Río Gallegos', 'Caleta Olivia', 'Pico Truncado', 'Puerto Deseado', 'Puerto San Julián', 'Río Turbio', 'El Calafate', 'Las Heras', 'Puerto Santa Cruz', 'Comandante Luis Piedra Buena', '28 de Noviembre', 'Perito Moreno', 'Gobernador Gregores'],
    'Santa Fe': ['Santa Fe', 'Rosario', 'Rafaela', 'Venado Tuerto', 'Reconquista', 'Villa Constitución', 'Casilda', 'San Lorenzo', 'Esperanza', 'Santo Tomé', 'Gálvez', 'Firmat', 'Cañada de Gómez', 'Vera', 'San Javier', 'Rufino', 'Tostado', 'Calchaquí', 'Las Rosas', 'Funes', 'Capitán Bermúdez', 'Arroyo Seco', 'Villa Gobernador Gálvez'],
    'Santiago del Estero': ['Santiago del Estero', 'La Banda', 'Termas de Río Hondo', 'Añatuya', 'Frías', 'Monte Quemado', 'Fernández', 'Suncho Corral', 'Quimilí', 'Clodomira', 'Pinto', 'Loreto', 'Bandera', 'Villa Ojo de Agua'],
    'Tierra del Fuego': ['Ushuaia', 'Río Grande', 'Tolhuin'],
    'Tucumán': ['San Miguel de Tucumán', 'Yerba Buena', 'Tafí Viejo', 'Banda del Río Salí', 'Concepción', 'Aguilares', 'Monteros', 'Famaillá', 'Alderetes', 'Simoca', 'Juan Bautista Alberdi', 'Bella Vista', 'Trancas', 'Burruyacú', 'Tafí del Valle', 'Graneros', 'La Cocha']
};

// Generar años (desde 1980 hasta 2025)
const añoSelect = document.getElementById('año_auto');
for (let año = 2025; año >= 1980; año--) {
    const option = document.createElement('option');
    option.value = año;
    option.textContent = año;
    añoSelect.appendChild(option);
}

// Cambiar modelos según la marca seleccionada
document.getElementById('marca_auto').addEventListener('change', function() {
    const marca = this.value;
    const modeloSelect = document.getElementById('modelo_auto');
    
    modeloSelect.innerHTML = '<option value="">Selecciona un modelo</option>';
    
    if (marca && modelosPorMarca[marca]) {
        modelosPorMarca[marca].forEach(modelo => {
            const option = document.createElement('option');
            option.value = modelo;
            option.textContent = modelo;
            modeloSelect.appendChild(option);
        });
    }
});

// Cambiar repuestos según la categoría seleccionada
document.getElementById('categoria_repuesto').addEventListener('change', function() {
    const categoria = this.value;
    const repuestoSelect = document.getElementById('repuesto_especifico');
    
    repuestoSelect.innerHTML = '<option value="">Selecciona un repuesto</option>';
    
    if (categoria && repuestosPorCategoria[categoria]) {
        repuestosPorCategoria[categoria].forEach(repuesto => {
            const option = document.createElement('option');
            option.value = repuesto;
            option.textContent = repuesto;
            repuestoSelect.appendChild(option);
        });
    }
});

// ===== FUNCIONES PARA PROVINCIAS Y LOCALIDADES =====
const provincias = Object.keys(localidadesPorProvincia).sort();

// Función para cargar provincias en un select
function cargarProvincias(selectElement) {
    selectElement.innerHTML = '<option value="">Selecciona una provincia</option>';
    provincias.forEach(provincia => {
        const option = document.createElement('option');
        option.value = provincia;
        option.textContent = provincia;
        selectElement.appendChild(option);
    });
}

// Función para cargar localidades según la provincia seleccionada
function cargarLocalidades(provincia, selectElement) {
    selectElement.innerHTML = '<option value="">Selecciona una localidad</option>';
    
    if (provincia && localidadesPorProvincia[provincia]) {
        localidadesPorProvincia[provincia].forEach(localidad => {
            const option = document.createElement('option');
            option.value = localidad;
            option.textContent = localidad;
            selectElement.appendChild(option);
        });
    }
}

// Inicializar selectores de provincia y localidad
const zonaSelect = document.getElementById('zona');
const localidadSelect = document.getElementById('localidad');

// Cargar provincias al iniciar
cargarProvincias(zonaSelect);

// Evento para cambiar localidades cuando se selecciona una provincia
zonaSelect.addEventListener('change', function() {
    const provinciaSeleccionada = this.value;
    cargarLocalidades(provinciaSeleccionada, localidadSelect);
});

// Navegación entre pasos
let currentStep = 1;
const totalSteps = 3; // CAMBIADO DE 4 A 3

function showStep(step) {
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    document.querySelector(`.step[data-step="${step}"]`).classList.add('active');

    document.querySelectorAll('.progress-step').forEach(s => {
        const stepNum = parseInt(s.dataset.step);
        s.classList.remove('active', 'completed');
        if (stepNum < step) {
            s.classList.add('completed');
        } else if (stepNum === step) {
            s.classList.add('active');
        }
    });

    document.getElementById('prevBtn').style.display = step === 1 ? 'none' : 'block';
    document.getElementById('nextBtn').style.display = step === totalSteps ? 'none' : 'block';
    document.getElementById('submitBtn').style.display = step === totalSteps ? 'block' : 'none';
}

function validateStep(step) {
    const currentStepElement = document.querySelector(`.step[data-step="${step}"]`);
    const requiredFields = currentStepElement.querySelectorAll('[required]');
    
    for (let field of requiredFields) {
        // Para campos select, verificar que el valor no sea vacío
        if (field.tagName === 'SELECT') {
            if (!field.value || field.value === '') {
                field.focus();
                alert('Por favor completa todos los campos obligatorios');
                return false;
            }
        } else {
            // Para inputs de texto
            if (!field.value || !field.value.trim()) {
                field.focus();
                alert('Por favor completa todos los campos obligatorios');
                return false;
            }
        }
    }
    return true;
}

document.getElementById('nextBtn').addEventListener('click', () => {
    if (validateStep(currentStep)) {
        if (currentStep < totalSteps) {
            currentStep++;
            showStep(currentStep);
        }
    }
});

document.getElementById('prevBtn').addEventListener('click', () => {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
    }
});

// IMPORTANTE: Manejar el submit del formulario
document.getElementById('submitBtn').addEventListener('click', function(e) {
    e.preventDefault(); // Prevenir el comportamiento por defecto
    
    if (validateStep(currentStep)) {
        // Si la validación pasa, enviar el formulario
        document.getElementById('compraForm').submit();
    }
});

// Inicializar en el paso 1
showStep(1);