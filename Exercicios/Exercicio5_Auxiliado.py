# Câmera e Iluminação - Múltiplas Luzes para CG em Tempo Real
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import ctypes
import math

Window          = None
Shader_programm = None
Vao_cubo        = None
Vao_esfera      = None
Num_vertices_esfera = 0

WIDTH  = 800
HEIGHT = 600

# Câmera FPS
Cam_speed = 10.0
Cam_pos   = np.array([0.0, 0.0, 2.0], dtype=np.float32)
Cam_yaw   =  -90.0
Cam_pitch =  0.0

lastX, lastY   = WIDTH / 2, HEIGHT / 2
primeiro_mouse = True
Tempo_entre_frames = 0.0

# -----------------------------
# Variáveis de Controle das Luzes
# -----------------------------
light1_on = True
light2_on = True
light3_on = True

def redimensionaCallback(window, w, h):
    global WIDTH, HEIGHT
    WIDTH  = w
    HEIGHT = h

def mouse_callback(window, xpos, ypos):
    global lastX, lastY, primeiro_mouse, Cam_yaw, Cam_pitch

    if primeiro_mouse:
        lastX, lastY   = xpos, ypos
        primeiro_mouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos
    lastX, lastY = xpos, ypos

    sensibilidade = 0.1
    Cam_yaw   += xoffset * sensibilidade
    Cam_pitch += yoffset * sensibilidade

    Cam_pitch = max(-89.0, min(89.0, Cam_pitch))

def key_callback(window, key, scancode, action, mods):
    global light1_on, light2_on, light3_on
    if action == glfw.PRESS:
        if key == glfw.KEY_1:
            light1_on = not light1_on
            print("Luz 1:", "LIGADA" if light1_on else "DESLIGADA")
        elif key == glfw.KEY_2:
            light2_on = not light2_on
            print("Luz 2:", "LIGADA" if light2_on else "DESLIGADA")
        elif key == glfw.KEY_3:
            light3_on = not light3_on
            print("Luz 3:", "LIGADA" if light3_on else "DESLIGADA")
            
    return
    
def inicializaOpenGL():
    global Window
    glfw.init()
    Window = glfw.create_window(WIDTH, HEIGHT, 'Multiplas Luzes - CG em Tempo Real', None, None)
    if not Window:
        glfw.terminate()
        exit()   
    glfw.make_context_current(Window)
    
    glfw.set_input_mode(Window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.set_cursor_pos_callback(Window, mouse_callback)
    glfw.set_window_size_callback(Window, redimensionaCallback)
    glfw.set_key_callback(Window, key_callback)

def inicializaCubo():
    global Vao_cubo
    pontos = [
         0.5,  0.5,  0.5,   0, 0, 1,
         0.5, -0.5,  0.5,   0, 0, 1,
        -0.5, -0.5,  0.5,   0, 0, 1,
         0.5,  0.5,  0.5,   0, 0, 1,
        -0.5, -0.5,  0.5,   0, 0, 1,
        -0.5,  0.5,  0.5,   0, 0, 1,

         0.5,  0.5, -0.5,   0, 0,-1,
         0.5, -0.5, -0.5,   0, 0,-1,
        -0.5, -0.5, -0.5,   0, 0,-1,
         0.5,  0.5, -0.5,   0, 0,-1,
        -0.5, -0.5, -0.5,   0, 0,-1,
        -0.5,  0.5, -0.5,   0, 0,-1,

        -0.5, -0.5,  0.5,  -1, 0, 0,
        -0.5,  0.5,  0.5,  -1, 0, 0,
        -0.5, -0.5, -0.5,  -1, 0, 0,
        -0.5, -0.5, -0.5,  -1, 0, 0,
        -0.5,  0.5, -0.5,  -1, 0, 0,
        -0.5,  0.5,  0.5,  -1, 0, 0,

         0.5, -0.5,  0.5,   1, 0, 0,
         0.5,  0.5,  0.5,   1, 0, 0,
         0.5, -0.5, -0.5,   1, 0, 0,
         0.5, -0.5, -0.5,   1, 0, 0,
         0.5,  0.5, -0.5,   1, 0, 0,
         0.5,  0.5,  0.5,   1, 0, 0,

        -0.5, -0.5,  0.5,   0,-1, 0,
         0.5, -0.5,  0.5,   0,-1, 0,
         0.5, -0.5, -0.5,   0,-1, 0,
         0.5, -0.5, -0.5,   0,-1, 0,
        -0.5, -0.5, -0.5,   0,-1, 0,
        -0.5, -0.5,  0.5,   0,-1, 0,

        -0.5,  0.5,  0.5,   0, 1, 0,
         0.5,  0.5,  0.5,   0, 1, 0,
         0.5,  0.5, -0.5,   0, 1, 0,
         0.5,  0.5, -0.5,   0, 1, 0,
        -0.5,  0.5, -0.5,   0, 1, 0,
        -0.5,  0.5,  0.5,   0, 1, 0,
    ]
    pontos = np.array(pontos, dtype=np.float32)
    Vao_cubo = glGenVertexArrays(1)
    glBindVertexArray(Vao_cubo)
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, pontos, GL_STATIC_DRAW)
    stride = 6 * 4
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

def inicializaEsfera():
    global Vao_esfera, Num_vertices_esfera
    points = []
    stacks, sectors, radius = 30, 30, 0.5
    PI = math.pi

    for i in range(stacks):
        phi1 = PI * i / stacks
        phi2 = PI * (i + 1) / stacks

        for j in range(sectors):
            theta1 = 2.0 * PI * j / sectors
            theta2 = 2.0 * PI * (j + 1) / sectors

            def add_vertex(p, t):
                x = radius * math.sin(p) * math.cos(t)
                y = radius * math.cos(p)
                z = radius * math.sin(p) * math.sin(t)
                points.extend([x, y, z])
                points.extend([x / radius, y / radius, z / radius])

            add_vertex(phi1, theta1)
            add_vertex(phi2, theta1)
            add_vertex(phi1, theta2)
            add_vertex(phi1, theta2)
            add_vertex(phi2, theta1)
            add_vertex(phi2, theta2)

    Num_vertices_esfera = len(points) // 6
    points_data = np.array(points, dtype=np.float32)
    Vao_esfera = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(Vao_esfera)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, points_data.nbytes, points_data, GL_STATIC_DRAW)
    float_size = ctypes.sizeof(ctypes.c_float)
    stride = 6 * float_size
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * float_size))
    glEnableVertexAttribArray(1)
    glBindVertexArray(0)

def inicializaShaders():
    global Shader_programm

    vertex_shader = """
        #version 450
        layout(location = 0) in vec3 vertex_posicao;
        layout(location = 1) in vec3 vertex_normal;

        uniform mat4 transform, view, proj;

        out vec3 fragPos;
        out vec3 normal;

        void main() {
            vec4 worldPos = transform * vec4(vertex_posicao, 1.0);
            fragPos = worldPos.xyz;
            normal = mat3(transpose(inverse(transform))) * vertex_normal;
            gl_Position = proj * view * worldPos;
        }
    """

    fragment_shader = """
        #version 450
        in vec3 fragPos;
        in vec3 normal;

        out vec4 frag_colour;

        // Três fontes de luz independentes
        uniform vec3 lightPos1;
        uniform vec3 lightPos2;
        uniform vec3 lightPos3;

        uniform vec3 lightColor1;
        uniform vec3 lightColor2;
        uniform vec3 lightColor3;
        
        // Flags de controle de estado (ligado = 1.0, desligado = 0.0)
        uniform float lightOn1;
        uniform float lightOn2;
        uniform float lightOn3;

        // Propriedades do material
        uniform vec3 objectColor;
        uniform float Ka;
        uniform float Kd;
        uniform float Ks;
        uniform float shininess;

        // Atenuação das três fontes
        uniform float Kc1, Kl1, Kq1;
        uniform float Kc2, Kl2, Kq2;
        uniform float Kc3, Kl3, Kq3;
        
        uniform vec3 viewPos;

        vec3 calculaLuz(vec3 lPos, vec3 lColor, float lOn, float Kc, float Kl, float Kq, vec3 N, vec3 V) {
            if (lOn < 0.5) return vec3(0.0);

            vec3 L = normalize(lPos - fragPos);
            vec3 R = reflect(-L, N);

            // Ambiente
            vec3 ambient = Ka * lColor;

            // Difuso
            float diff = max(dot(N, L), 0.0);
            vec3 diffuse = Kd * diff * lColor;

            // Especular
            float spec = pow(max(dot(V, R), 0.0), shininess);
            vec3 specular = Ks * spec * lColor;

            // Atenuação
            float d = length(lPos - fragPos);
            float attenuation = 1.0 / (Kc + Kl * d + Kq * (d * d));

            return (ambient + diffuse) * attenuation + (specular * attenuation);
        }

        void main() {
            vec3 N = normalize(normal);
            vec3 V = normalize(viewPos - fragPos);

            vec3 totalLight = vec3(0.0);

            totalLight += calculaLuz(lightPos1, lightColor1, lightOn1, Kc1, Kl1, Kq1, N, V);
            totalLight += calculaLuz(lightPos2, lightColor2, lightOn2, Kc2, Kl2, Kq2, N, V);
            totalLight += calculaLuz(lightPos3, lightColor3, lightOn3, Kc3, Kl3, Kq3, N, V);

            vec3 result = totalLight * objectColor;
            frag_colour = vec4(result, 1.0);
        }
    """

    vs = OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
    fs = OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    Shader_programm = OpenGL.GL.shaders.compileProgram(vs, fs)
    glDeleteShader(vs)
    glDeleteShader(fs)

def transformacaoGenerica(Tx, Ty, Tz, Sx, Sy, Sz, Rx, Ry, Rz):
    translacao = np.array([
        [1, 0, 0, Tx],
        [0, 1, 0, Ty],
        [0, 0, 1, Tz],
        [0, 0, 0,  1]
    ], dtype=np.float32)

    rx, ry, rz = np.radians([Rx, Ry, Rz])
    rotacaoX = np.array([
        [1,           0,            0, 0],
        [0, np.cos(rx), -np.sin(rx), 0],
        [0, np.sin(rx),  np.cos(rx), 0],
        [0,           0,            0, 1]
    ], dtype=np.float32)

    rotacaoY = np.array([
        [ np.cos(ry), 0, np.sin(ry), 0],
        [           0, 1,           0, 0],
        [-np.sin(ry), 0, np.cos(ry), 0],
        [           0, 0,           0, 1]
    ], dtype=np.float32)

    rotacaoZ = np.array([
        [np.cos(rz), -np.sin(rz), 0, 0],
        [np.sin(rz),  np.cos(rz), 0, 0],
        [          0,           0, 1, 0],
        [          0,           0, 0, 1]
    ], dtype=np.float32)

    escala = np.array([
        [Sx,  0,  0, 0],
        [ 0, Sy,  0, 0],
        [ 0,  0, Sz, 0],
        [ 0,  0,  0, 1]
    ], dtype=np.float32)

    transformacaoFinal = translacao @ rotacaoZ @ rotacaoY @ rotacaoX @ escala
    loc = glGetUniformLocation(Shader_programm, "transform")
    glUniformMatrix4fv(loc, 1, GL_TRUE, transformacaoFinal)

def especificaMatrizVisualizacao():
    frente = np.array([
        np.cos(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch))
    ], dtype=np.float32)
    frente /= np.linalg.norm(frente)

    cima   = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    s = np.cross(frente, cima); s /= np.linalg.norm(s)
    u = np.cross(s, frente)

    view = np.identity(4, dtype=np.float32)
    view[0, :3] =  s
    view[1, :3] =  u
    view[2, :3] = -frente
    view[0,  3] = -np.dot(s,      Cam_pos)
    view[1,  3] = -np.dot(u,      Cam_pos)
    view[2,  3] =  np.dot(frente, Cam_pos)

    transformLoc = glGetUniformLocation(Shader_programm, "view")
    glUniformMatrix4fv(transformLoc, 1, GL_TRUE, view)

def especificaMatrizProjecao():
    znear, zfar = 0.1, 100.0
    fov = np.radians(67.0)
    aspecto = WIDTH / HEIGHT

    a = 1.0 / (np.tan(fov / 2) * aspecto)
    b = 1.0 /  np.tan(fov / 2)
    c = (zfar + znear) / (znear - zfar)
    d = (2 * znear * zfar) / (znear - zfar)

    projecao = np.array([
        [a,   0.0, 0.0,  0.0],
        [0.0, b,   0.0,  0.0],
        [0.0, 0.0, c,    d  ],
        [0.0, 0.0, -1.0, 1.0]
    ], dtype=np.float32)

    transformLoc = glGetUniformLocation(Shader_programm, "proj")
    glUniformMatrix4fv(transformLoc, 1, GL_TRUE, projecao)

def inicializaCamera():
    especificaMatrizVisualizacao()
    especificaMatrizProjecao()

def defineMaterial(r, g, b, ka, kd, ks, shininess):
    glUniform3f(glGetUniformLocation(Shader_programm, "objectColor"), r, g, b)
    glUniform1f(glGetUniformLocation(Shader_programm, "Ka"),          ka)
    glUniform1f(glGetUniformLocation(Shader_programm, "Kd"),          kd)
    glUniform1f(glGetUniformLocation(Shader_programm, "Ks"),          ks)
    glUniform1f(glGetUniformLocation(Shader_programm, "shininess"),   shininess)

def trataTeclado():
    global Cam_pos
    velocidade = Cam_speed * Tempo_entre_frames
    frente = np.array([
        np.cos(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_pitch)),
        np.sin(np.radians(Cam_yaw)) * np.cos(np.radians(Cam_pitch))
    ], dtype=np.float32)
    frente /= np.linalg.norm(frente)

    direita = np.cross(frente, np.array([0.0, 1.0, 0.0], dtype=np.float32))
    direita /= np.linalg.norm(direita)

    if glfw.get_key(Window, glfw.KEY_W) == glfw.PRESS: Cam_pos += frente * velocidade
    if glfw.get_key(Window, glfw.KEY_S) == glfw.PRESS: Cam_pos -= frente * velocidade
    if glfw.get_key(Window, glfw.KEY_A) == glfw.PRESS: Cam_pos -= direita * velocidade
    if glfw.get_key(Window, glfw.KEY_D) == glfw.PRESS: Cam_pos += direita * velocidade
    if glfw.get_key(Window, glfw.KEY_ESCAPE) == glfw.PRESS: glfw.set_window_should_close(Window, True)

def inicializaRenderizacao():
    global Tempo_entre_frames
    tempo_anterior = glfw.get_time()
    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(Window):
        tempo_atual        = glfw.get_time()
        Tempo_entre_frames = tempo_atual - tempo_anterior
        tempo_anterior     = tempo_atual

        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, WIDTH, HEIGHT)

        glUseProgram(Shader_programm)
        inicializaCamera()

        # Envia a posição da câmera
        glUniform3fv(glGetUniformLocation(Shader_programm, "viewPos"), 1, Cam_pos)

        # -----------------------------
        # Configuração das Luzes
        # -----------------------------
        # Luz 1: Vermelha, fixa e com curto alcance
        glUniform3f(glGetUniformLocation(Shader_programm, "lightPos1"), 2.0, 0.0, 1.0)
        glUniform3f(glGetUniformLocation(Shader_programm, "lightColor1"), 1.0, 0.0, 0.0)
        glUniform1f(glGetUniformLocation(Shader_programm, "Kc1"), 1.0)
        glUniform1f(glGetUniformLocation(Shader_programm, "Kl1"), 0.4)
        glUniform1f(glGetUniformLocation(Shader_programm, "Kq1"), 0.3)
        glUniform1f(glGetUniformLocation(Shader_programm, "lightOn1"), float(light1_on))

        # Luz 2: Verde, rotativa (Animação - baseada no tempo)
        luz2_x = 2.5 * math.sin(tempo_atual)
        luz2_z = 2.5 * math.cos(tempo_atual)
        glUniform3f(glGetUniformLocation(Shader_programm, "lightPos2"), luz2_x, 1.0, luz2_z)
        glUniform3f(glGetUniformLocation(Shader_programm, "lightColor2"), 0.0, 1.0, 0.0)
        glUniform1f(glGetUniformLocation(Shader_programm, "Kc2"), 1.0)
        glUniform1f(glGetUniformLocation(Shader_programm, "Kl2"), 0.09)
        glUniform1f(glGetUniformLocation(Shader_programm, "Kq2"), 0.032)
        glUniform1f(glGetUniformLocation(Shader_programm, "lightOn2"), float(light2_on))

        # Luz 3: Azul, estática e com longo alcance
        glUniform3f(glGetUniformLocation(Shader_programm, "lightPos3"), -2.0, -1.0, 2.0)
        glUniform3f(glGetUniformLocation(Shader_programm, "lightColor3"), 0.0, 0.3, 1.0)
        glUniform1f(glGetUniformLocation(Shader_programm, "Kc3"), 1.0)
        glUniform1f(glGetUniformLocation(Shader_programm, "Kl3"), 0.05)
        glUniform1f(glGetUniformLocation(Shader_programm, "Kq3"), 0.01)
        glUniform1f(glGetUniformLocation(Shader_programm, "lightOn3"), float(light3_on))

        # Material do Objeto
        defineMaterial(0.8, 0.8, 0.8, 0.1, 0.7, 0.5, 32.0)

        # Renderiza a esfera
        glBindVertexArray(Vao_esfera)
        transformacaoGenerica(0, 0, 0, 1, 1, 1, 0, 0, 0)
        glDrawArrays(GL_TRIANGLES, 0, Num_vertices_esfera)

        glfw.swap_buffers(Window)
        glfw.poll_events()
        trataTeclado()

    glfw.terminate()

def main():
    inicializaOpenGL()
    inicializaCubo()
    inicializaEsfera()
    inicializaShaders()
    inicializaRenderizacao()

if __name__ == "__main__":
    main()