<img src="demo_sistemaSolar.gif" width="700px">

```text
====================================================================
SIMULACAO DO SISTEMA SOLAR
Estudo de renderizacao em tempo real usando OpenGL moderno
====================================================================

> RESUMO DO PROJETO:
Projeto desenvolvido em Python focado na construcao de um pipeline 
grafico do zero. A simulacao implementa a geracao parametrica de 
malhas 3D, calculos precisos de matrizes MVP (Model-View-Projection) 
para lidar com a hierarquia de transformacoes orbitais, e a escrita 
de Shaders GLSL customizados para iluminacao Blinn-Phong e tratamento 
avancado de texturas (incluindo Alpha Clipping).

--------------------------------------------------------------------
[/// 01. COMO_EXECUTAR ///]

> Dependencias requeridas_
  Execute o comando abaixo no console para instalar os modulos:
  $ pip install PyOpenGL PyOpenGL_accelerate glfw Pillow numpy

> Inicializacao_
  $ python Exercicio6.py

--------------------------------------------------------------------
[/// 02. TECNOLOGIAS_E_BIBLIOTECAS ///]

|-- PyOpenGL_     : Interface com API grafica e compilação de Shaders
|-- glfw_         : Gerenciador de janelas e inputs de hardware
|-- Pillow (PIL)_ : Descompressor de texturas 2D, 1D e Cubemaps
|-- numpy_        : Motor de algebra linear para as matrizes da cena

--------------------------------------------------------------------
[/// 03. CONTROLES_E_INTERACAO ///]

> NAVEGACAO_LIVRE:
  [W][A][S][D] : Movimentacao da camera (Frente, Esquerda, Tras, Direita)
  [MOUSE]      : Rotacao de visao (Pitch e Yaw)

> SISTEMA_DE_FOCO_ORBITAL (SNAP):
  [1] Sol         [2] Mercurio    [3] Venus       [4] Terra
  [5] Lua         [6] Marte       [7] Jupiter     [8] Saturno
  [9] Urano       [0] Netuno

> ENCERRAMENTO_DE_SESSAO:
  [ESC] : Fechar simulacao

--------------------------------------------------------------------
[/// 04. PARAMETROS_DE_ESCALA ///]

[CALCULO_DE_MASSA/RAIO]
> Formula adotada : raio_render = raio_real_em_km / 50000
> Aplicacao na malha :
  - Sol      : 13.927 u
  - Jupiter  :  1.430 u
  - Saturno  :  1.205 u
  - Terra    :  0.128 u
  - Lua      :  0.035 u

[CALCULO_DE_DISTANCIA_ORBITAL]
> Formula adotada : dist_render = dist_real_em_milhoes_de_km
> Aplicacao no pipeline :
  - Mercurio :   57.9 u
  - Venus    :  108.2 u
  - Terra    :  149.6 u
  - Netuno   : 4515.0 u
> Relacao de Satelite :
  - Lua orbita ancorada a Terra na distancia fixa de 0.384 u.

[SINCRONIZACAO_TEMPORAL]
> Aceleracao : 1 segundo real equivale a 10 dias orbitais simulados.

--------------------------------------------------------------------
[/// 05. BANCO_DE_ASSETS ///]

> Estrela, Planeta e Satelite : Mapas 2K. 
https://www.solarsystemscope.com/textures/
> Aneis de Saturno      : Textura 1D mapeada radialmente. 
https://www.solarsystemscope.com/textures/
> Skybox Estelar        : Cubemap continuo de 6 faces. 
https://opengameart.org/content/ulukais-space-skyboxes
====================================================================
```