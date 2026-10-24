Acción Kit_De_Analisis_Reutilizable Es
    Ambiente
        //Constantes
        N = 24;                 // cantidad de lecturas por sensor (24 horas)
        UMBRAL_ANOMALIA = 42.0; // umbral crítico para detección de anomalías
        LONG_MIN_RACHA = 3;     // longitud mínima de lecturas consecutivas

        
        lectura = registro
            sensor: entero;
            nro: entero;
            valor: real;
        fin_reg;

        arch_lecturas = ARCHIVO de lectura ordenado por sensor;
        vec_lecturas = ARREGLO [1..N] de real;

        csv: arch_lecturas;
        lecturas: vec_lecturas;
        v_max, v_min, v_prom: real;
        pos_ini_racha, pos_umbral, sensor_elegido,pos_max, pos_min: entero;
        hay_racha: logico;

        //lee el archivo secuencial de registros una sola vez, filtra por el sensor solicitado y almacena cada lectura en la posición de nro
        Procedimiento Cargar(var arch: arch_lecturas; id_sensor, n: entero; var a: vec_lecturas);
            Ambiente
                reg: lectura;
            Proceso
                ABRIR E(arch);
                LEER(arch, reg);
                MIENTRAS NFDA(arch) HACER
                    SI reg.sensor = id_sensor ENTONCES
                        SI (reg.nro >= 1) Y (reg.nro <= n) ENTONCES
                            a[reg.nro] := reg.valor;
                        FIN SI;
                    FIN SI;
                    LEER(arch, reg);
                FIN MIENTRAS;
                CERRAR(arch);
            fin_proc;

        //recorre el vector en una única pasada(O(N)). Calcula y retorna: valor máximo y posición, valor mínimo y su posición, y el promedio general.
        Procedimiento CalcularEstadisticas(a: vec_lecturas; n: entero; var pos_max, pos_min: entero; max_val, min_val, prom: real);
            Ambiente
                i: entero;
                suma: real;
            Proceso
                max_val := a[1];
                pos_max := 1;
                min_val := a[1];
                pos_min := 1;
                suma := a[1];

                PARA i := 2 HASTA n HACER
                    //busca el máximo
                    SI a[i] > max_val ENTONCES
                        max_val := a[i];
                        pos_max := i;
                    FIN SI;

                    //busca el mínimo
                    SI a[i] < min_val ENTONCES
                        min_val := a[i];
                        pos_min := i;
                    FIN SI;

                    suma := suma + a[i];
                FIN PARA;

                prom := suma / n;
            fin_proc;

        //busca la primera posición que supere un umbral declarado, si no encuentra retorna 0
        Procedimiento BuscarPorUmbral(a: vec_lecturas; n: entero; var pos_encontrada: entero; umbral: real);
            Ambiente
                i: entero;
                encontrado: logico;
            Proceso
                i := 1;
                encontrado := FALSO;
                pos_encontrada := 0;

                MIENTRAS (i <= n) Y (NO encontrado) HACER
                    SI a[i] > umbral ENTONCES
                        encontrado := VERDADERO;
                        pos_encontrada := i;
                    SINO
                        i := i + 1;
                    FIN SI;
                FIN MIENTRAS;
            fin_proc;

        //busca la primera secuencia continua de al menos long_min lecturas consecutivas que superen el umbral
        Procedimiento DetectarRacha(a: vec_lecturas; n: entero; long_min: entero; var pos_inicio: entero; umbral: real; hay_racha: logico);
            Ambiente
                i: entero;
                cont_racha: entero;
            Proceso
                i := 1;
                cont_racha := 0;
                hay_racha := FALSO;
                pos_inicio := 0;

                MIENTRAS (i <= n) Y (NO hay_racha) HACER
                    SI a[i] > umbral ENTONCES
                        cont_racha := cont_racha + 1;
                        SI cont_racha >= long_min ENTONCES
                            hay_racha := VERDADERO;
                            pos_inicio := i - long_min + 1;
                        FIN SI;
                    SINO
                        cont_racha := 0;
                    FIN SI;
                    i := i + 1;
                FIN MIENTRAS;
            fin_proc;

    
    Proceso

        sensor_elegido := 2; // Ejemplo: Sensor 2 (tiene una racha anómala inyectada)

        //carga lecturas del sensor seleccionado
        Cargar(csv, sensor_elegido, N, lecturas);

        //cálculo de estadísticas globales del sensor
        CalcularEstadisticas(lecturas, N, pos_max, pos_min, v_max, v_min, v_prom);
        ESCRIBIR("ESTADÍSTICAS SENSOR: ", sensor_elegido);
        ESCRIBIR("Temperatura máxima: ", v_max, " en la lectura ", pos_max);
        ESCRIBIR("Temperatura mínima: ", v_min, " en la lectura ", pos_min);
        ESCRIBIR("Temperatura promedio: ", v_prom);

        //búsqueda de primera lectura que supera el umbral
        BuscarPorUmbral(lecturas, N, UMBRAL_ANOMALIA, pos_umbral);
        SI pos_umbral <> 0 ENTONCES
            ESCRIBIR("Primera lectura sobre umbral detectada en nro: ", pos_umbral);
        SINO
            ESCRIBIR("Ninguna lectura superó el umbral.");
        FIN SI;

        //detección de racha continua de anomalías
        DetectarRacha(lecturas, N, LONG_MIN_RACHA, UMBRAL_ANOMALIA, pos_ini_racha, hay_racha);
        SI hay_racha ENTONCES
            ESCRIBIR("Racha anómala iniciada en la lectura nro: ", pos_ini_racha);
        SINO
            ESCRIBIR("No se encontraron rachas anómalas.");
        FIN SI;
FIN ACCION