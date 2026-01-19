
import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
from PIL import Image

class OpenGLEngine:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        # Initialize a hidden pygame window for GL context
        pygame.display.set_mode((1, 1), pygame.OPENGL | pygame.DOUBLEBUF | pygame.HIDDEN)
        
        self.shader = None
        self.vbo = None
        self._init_gl()
        
    def _init_gl(self):
        # Background color
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Create a simple quad that covers the screen
        self.vertices = np.array([
            -1.0, -1.0, 0.0,
             1.0, -1.0, 0.0,
             1.0,  1.0, 0.0,
            -1.0,  1.0, 0.0
        ], dtype=np.float32)
        
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        # Setup FBO
        self.fbo = glGenFramebuffers(1)
        self.texture = glGenTextures(1)
        self.depth_buffer = glGenRenderbuffers(1)
        self._setup_fbo_buffers()

    def _setup_fbo_buffers(self):
        print(f"[GL LOG] Setting up FBO buffers for size: {self.width}x{self.height}")
        
        # Resize hidden window as well to avoid driver limitations on FBO size
        try:
            pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.HIDDEN)
        except Exception as e:
            print(f"[GL ERROR] Failed to resize hidden window: {e}")

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        
        # Texture
        glBindTexture(GL_TEXTURE_2D, self.texture)
        # Re-allocate texture storage
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texture, 0)
        
        # Depth
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_buffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.depth_buffer)
        
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            print(f"[GL ERROR] FBO incomplete! Status: {status}")
        else:
            print(f"[GL LOG] FBO setup complete.")
            
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def load_shader(self, vertex_src, fragment_src):
        print("[GL LOG] Loading shaders...")
        try:
            shader = compileProgram(
                compileShader(vertex_src, GL_VERTEX_SHADER),
                compileShader(fragment_src, GL_FRAGMENT_SHADER)
            )
            self.shader = shader
            print("[GL LOG] Shaders compiled successfully.")
            return True
        except Exception as e:
            print(f"[GL ERROR] Shader compilation failed: {e}")
            return False
            
    def render_frame(self, time, audio_data):
        """Renders a frame using the current shader and returns it as a PIL Image."""
        # Detect size change
        # Usually handled by the visualizer.py updating self.width/height
        # But we need a local record to know when to recreate FBO
        if not hasattr(self, '_last_width') or self._last_width != self.width or self._last_height != self.height:
            self._setup_fbo_buffers()
            self._last_width = self.width
            self._last_height = self.height
        
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(0, 0, self.width, self.height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if not self.shader:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            return Image.new('RGB', (self.width, self.height), (20, 0, 0)) # Red tint for missing shader
            
        glUseProgram(self.shader)
        
        # Set Uniforms (with checks)
        u_time_loc = glGetUniformLocation(self.shader, "u_time")
        if u_time_loc != -1: glUniform1f(u_time_loc, time)
        
        u_res_loc = glGetUniformLocation(self.shader, "u_resolution")
        if u_res_loc != -1: glUniform2f(u_res_loc, float(self.width), float(self.height))
        
        # Audio uniform
        if audio_data is not None:
             audio_arr = np.array(audio_data, dtype=np.float32)
             u_audio_loc = glGetUniformLocation(self.shader, "u_audio")
             if u_audio_loc != -1:
                 # Check if the uniform array size matches (max 64)
                 glUniform1fv(u_audio_loc, min(len(audio_arr), 64), audio_arr[:64])
        
        # Draw Quad
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        position = glGetAttribLocation(self.shader, "position")
        if position != -1:
            glEnableVertexAttribArray(position)
            glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None)
            glDrawArrays(GL_QUADS, 0, 4)
            glDisableVertexAttribArray(position)
        else:
            # Fallback if position attribute name is different in shader (e.g. 'in_position')
            # Let's try to find it
            pass
        
        # Read back
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        try:
            data = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            img = Image.frombytes('RGB', (self.width, self.height), data)
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        except Exception as e:
            print(f"[GL ERROR] ReadPixels Error: {e}")
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            return Image.new('RGB', (self.width, self.height), (0, 20, 0)) # Green tint for read error

# Ultra-Reactive Psychedelic Fractal Shader
FRACTAL_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

// Better palette function
vec3 get_palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    vec2 uv0 = uv;
    vec3 finalColor = vec3(0.0);
    
    // Extract multi-band audio data
    float bass = u_audio[1] * 3.0;
    float mid = u_audio[10] * 2.5;
    float high = u_audio[40] * 4.0;
    float energy = (bass + mid + high) / 3.0;

    // Movement that shifts with audio
    float t = u_time * 0.2 + (bass * 0.05);

    // Fractal iteration
    for (float i = 0.0; i < 4.0; i++) {
        // Kaleidoscopic folding influenced by mids
        uv = abs(uv);
        uv -= 0.5 + (mid * 0.1);
        float angle = 0.5 + (high * 0.02);
        float s = sin(angle);
        float c = cos(angle);
        uv *= mat2(c, -s, s, c);
        
        // Iterative transformation
        uv = fract(uv * (1.2 + bass * 0.2)) - 0.5;

        float d = length(uv) * exp(-length(uv0));

        // Color shifts with high frequencies and iterations
        vec3 col = get_palette(
            length(uv0) + i * 0.4 + t, 
            vec3(0.5, 0.5, 0.5), 
            vec3(0.5, 0.5, 0.5), 
            vec3(1.0, 1.0, 1.0), 
            vec3(0.0 + high, 0.33, 0.67 + bass)
        );

        // Neon line effect
        d = sin(d * (8.0 + bass) + t * 2.0) / (8.0 + high);
        d = abs(d);
        d = pow(0.01 / d, 1.2);

        finalColor += col * d * (0.5 + energy);
    }
    
    // Vignette and contrast
    float mask = smoothstep(1.5, 0.5, length(uv0));
    finalColor *= mask;
    
    // Extreme high-end flash
    finalColor += high * 0.3 * vec3(0.1, 0.4, 1.0);

    fragColor = vec4(finalColor, 1.0);
}
"""

# Neural Liquid Shader (Psychedelic Melting)
LIQUID_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    
    float bass = u_audio[2] * 2.0;
    float mid = u_audio[12] * 2.0;
    float high = u_audio[35] * 3.0;
    
    float t = u_time * 0.5;
    
    // Fluid displacement
    for(float i = 1.0; i < 6.0; i++) {
        uv.x += sin(uv.y * i * 3.0 + t + bass) * 0.1 / i;
        uv.y += cos(uv.x * i * 3.0 + t + mid) * 0.1 / i;
    }
    
    // Color generation
    vec3 col;
    col.r = 0.5 + 0.5 * sin(uv.x * 5.0 + t + 0.0 + high);
    col.g = 0.5 + 0.5 * sin(uv.y * 5.0 + t + 2.0 + bass);
    col.b = 0.5 + 0.5 * sin((uv.x + uv.y) * 5.0 + t + 4.0 + mid);
    
    // Edge highlights
    float ripple = sin(uv.x * 50.0 + uv.y * 50.0 + t * 10.0);
    col += vec3(1.0) * max(0.0, ripple) * 0.2 * high;
    
    // Negative pulses
    if(bass > 0.8) col = 1.0 - col;

    fragColor = vec4(col, 1.0);
}
"""

# Quantum Bloom Shader (Recursive Symmetry)
BLOOM_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

vec3 palette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.3, 0.2, 0.2);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    vec2 uv0 = uv;
    vec3 finalColor = vec3(0.0);
    
    float bass = u_audio[1] * 2.5;
    float high = u_audio[45] * 3.0;
    
    float angle = u_time * 0.2;
    mat2 rot = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
    uv *= rot;

    for (float i = 0.0; i < 3.0; i++) {
        uv = abs(uv) - 0.5 - (bass * 0.05);
        uv *= 1.3 + (high * 0.02);
        uv *= rot;
        
        float d = length(uv) * exp(-length(uv0));
        vec3 col = palette(length(uv0) + i * 0.4 + u_time * 0.4);

        d = sin(d * 8.0 + u_time) / 8.0;
        d = abs(d);
        d = pow(0.01 / d, 1.2);

        finalColor += col * d;
    }
    
    finalColor *= (1.2 + bass * 0.5);
    fragColor = vec4(finalColor, 1.0);
}
"""

# Organic Cells Shader (Voronoi Audio-Growth)
CELLS_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

vec2 hash2(vec2 p) {
    return fract(sin(vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))))*43758.5453);
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    uv *= 3.0; // zoom level
    
    float bass = u_audio[2] * 2.0;
    
    vec2 i_uv = floor(uv);
    vec2 f_uv = fract(uv);
    
    float m_dist = 1.0;
    for (int y= -1; y<=1; y++) {
        for (int x= -1; x<=1; x++) {
            vec2 neighbor = vec2(float(x),float(y));
            vec2 point = hash2(i_uv + neighbor);
            
            // Animate point with audio
            point = 0.5 + 0.5*sin(u_time + 6.2831*point + bass);
            
            vec2 diff = neighbor + point - f_uv;
            float dist = length(diff);
            m_dist = min(m_dist, dist);
        }
    }
    
    vec3 col = vec3(m_dist);
    col *= mix(vec3(0.1, 0.5, 0.2), vec3(0.8, 0.2, 0.1), m_dist + bass * 0.5);
    
    // Cell borders
    col += smoothstep(0.02, 0.0, abs(m_dist - 0.5)) * vec3(1.0, 1.0, 0.0) * bass;

    fragColor = vec4(col, 1.0);
}
"""

# Hyperwarp Tunnel Shader (Extreme Psychedelic Warp - ENHANCED)
HYPERWARP_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

vec3 palette(float t) {
    // Ultra-vibrant, high-contrast palette
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.263, 0.416, 0.557);
    return a + b * cos(6.28318 * (c * t + d + u_time * 0.5));
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    
    float bass = u_audio[1] * 3.0;
    float mid = u_audio[15] * 2.5;
    float high = u_audio[40] * 4.0;
    
    // Extreme warping
    float strength = 1.0 + bass;
    uv *= 1.0 + sin(length(uv) * 15.0 - u_time * 8.0) * 0.2 * strength;
    
    float a = atan(uv.y, uv.x);
    float r = length(uv);
    
    float depth = 1.0 / (r + 0.001);
    float x = a / 3.14159;
    float y = depth + u_time * (8.0 + bass * 4.0);
    
    vec3 col = vec3(0.0);
    
    for(float i=1.0; i<=4.0; i++) {
        vec2 p = vec2(x * i + sin(u_time * 0.2), y * 0.3);
        float pattern = sin(p.y * 12.0 + sin(p.x * 25.0 + u_time * 2.0)) * 0.5 + 0.5;
        pattern = pow(pattern, 2.5);
        
        // Luminiscent colors
        vec3 layerCol = palette(y * 0.05 + i * 0.25 + bass * 0.1);
        col += layerCol * pattern * (1.5 / (r * 3.0 + 0.2)) * (0.8 + mid);
    }
    
    // Core flare
    col += palette(u_time) * pow(0.15 / r, 1.8) * (1.5 + high);
    
    // Saturation boost
    col = pow(col, vec3(0.8));
    
    fragColor = vec4(col, 1.0);
}
"""

# Mandelbrot Trip Shader (Recursive Smooth Zoom - ENHANCED)
MANDELBROT_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

vec3 palette(float t) {
    // Psychedelic smooth palette
    return 0.5 + 0.5 * cos(6.28318 * (vec3(1.0, 0.7, 0.3) * t + vec3(0.0, 0.15, 0.2)));
}

void main() {
    float bass = u_audio[1] * 2.0;
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    
    // Much smoother zoom
    float z_time = u_time * 0.4;
    float zoom = pow(0.5, mod(z_time, 15.0));
    vec2 center = vec2(-0.745, 0.186) + vec2(sin(u_time * 0.1), cos(u_time * 0.1)) * 0.001;
    vec2 c = uv * zoom + center;
    
    vec2 z = vec2(0.0);
    float iter = 0.0;
    for(float i=0.0; i<150.0; i++) {
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
        if(length(z) > 16.0) break; // Escape radius high for smoothing
        iter += 1.0;
    }
    
    if(iter == 150.0) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
    } else {
        // Smooth coloring
        float slt = iter - log2(log2(dot(z,z))) + 4.0;
        vec3 col = palette(slt * 0.05 + u_time * 0.1 + bass * 0.05);
        
        // Add glow near edges
        col *= (1.0 + bass * 0.3);
        fragColor = vec4(col, 1.0);
    }
}
"""

# Electric Storm Shader (Procedural Lightning & Clouds - ENHANCED)
STORM_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f*f*(3.0-2.0*f);
    return mix(mix(hash(i), hash(i+vec2(1.0,0.0)), f.x),
               mix(hash(i+vec2(0.0,1.0)), hash(i+vec2(1.0,1.0)), f.x), f.y);
}
float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 5; i++) { v += a * noise(p); p *= 2.0; a *= 0.5; }
    return v;
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    float high = u_audio[45] * 4.0;
    float bass = u_audio[1] * 2.0;

    // Dark cloud background
    float clouds = fbm(uv * 2.0 + u_time * 0.2);
    vec3 col = vec3(0.05, 0.05, 0.1) * clouds;
    
    // Multiple lightning bolts
    for(float i=0.0; i<3.0; i++) {
        float t = u_time * 5.0 + i * 20.0;
        if(hash(vec2(floor(t))) > 0.8 - high * 0.1) {
            float x_offset = (hash(vec2(i, floor(t))) - 0.5) * 1.5;
            // Lightning path using FBM
            float bolt_x = x_offset + (fbm(vec2(uv.y * 2.0, t)) - 0.5) * 0.5;
            float dist = abs(uv.x - bolt_x);
            
            float intensity = 0.01 / (dist + 0.005);
            vec3 boltCol = vec3(0.7, 0.8, 1.0) * intensity;
            col += boltCol;
            
            // Background flash
            col += vec3(0.2, 0.3, 0.5) * 0.5;
        }
    }
    
    // Bass lightning impact (bottom flash)
    col += vec3(0.1, 0.2, 0.4) * bass * smoothstep(0.0, -1.0, uv.y);
    
    fragColor = vec4(col, 1.0);
}
"""

# DNA Helix Shader (Hyper-Detailed 3D - ENHANCED)
DNA_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    float bass = u_audio[1] * 2.5;
    float mid = u_audio[15] * 2.0;
    float high = u_audio[40] * 3.0;

    vec3 col = vec3(0.0);
    
    for(float i=0.0; i<60.0; i++) {
        float layer = i / 60.0;
        float angle = u_time * 2.0 + i * 0.3 + bass * 0.2;
        
        float x = sin(angle) * 0.6;
        float z = cos(angle); // Z depth
        
        float y = (layer - 0.5) * 2.5;
        
        // Two Strand spheres
        float d1 = length(uv - vec2(x, y));
        float d2 = length(uv - vec2(-x, y));
        
        // Depth-based size and glow
        float glow1 = 0.008 / (d1 + 0.001);
        float glow2 = 0.008 / (d2 + 0.001);
        
        // Color strands differently
        vec3 c1 = vec3(0.0, 0.8, 1.0) * (z + 1.2);
        vec3 c2 = vec3(1.0, 0.2, 0.8) * (1.2 - z);
        
        col += c1 * glow1 * (0.8 + high * 0.1);
        col += c2 * glow2 * (0.8 + high * 0.1);
        
        // Rungs (connecting lines)
        vec2 p1 = vec2(x, y);
        vec2 p2 = vec2(-x, y);
        vec2 pa = uv - p1, ba = p2 - p1;
        float h = clamp(dot(pa,ba)/dot(ba,ba), 0.0, 1.0);
        float line_d = length(pa - ba*h);
        
        if (int(i) % 3 == 0) {
            col += vec3(0.5) * (0.002 / (line_d + 0.001)) * (mid + 0.5);
        }
    }
    
    // Soft atmospheric glow
    col += vec3(0.1, 0.05, 0.15) * bass;
    
    fragColor = vec4(col, 1.0);
}
"""

# Audio Matrix Shader (Digital Rain - ENHANCED)
MATRIX_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }

void main() {
    // 3D-ish perspective for the rain
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    uv.y += uv.y * abs(uv.x) * 0.5; // Slight warp
    
    float bass = u_audio[1] * 3.0;
    float high = u_audio[45] * 4.0;
    
    float cols = 60.0;
    float col_idx = floor(uv.x * cols);
    
    // Falling speed synced to audio energy
    float fall_speed = hash(vec2(col_idx)) * 2.0 + 1.0 + bass * 4.0;
    float y_pos = uv.y + u_time * fall_speed;
    float cell_y = floor(y_pos * 20.0);
    
    // Character intensity
    float h = hash(vec2(col_idx, cell_y));
    float trail = mod(y_pos * 20.0, 20.0) / 20.0;
    
    // Matrix color (neon green but with high frequency jitters)
    vec3 base_col = vec3(0.0, 1.0, 0.3);
    if(high > 0.7 && hash(vec2(u_time)) > 0.9) base_col = vec3(0.8, 1.0, 0.9); // Glitch white
    
    float brightness = pow(trail, 4.0) * step(0.4, h);
    vec3 col = base_col * brightness * (1.0 + high);
    
    // Horizon fade
    col *= smoothstep(2.0, 0.0, abs(uv.y));
    
    fragColor = vec4(col, 1.0);
}
"""

# Infinity Mirrors Shader (Kaleidoscopic Geometry - ENHANCED & BALANCED)
MIRROR_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

vec3 get_palette(float t) {
    // Elegant, less blinding palette
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.3, 0.2, 0.2);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    float bass = u_audio[1] * 2.5;
    float high = u_audio[45] * 3.0;

    vec3 final_col = vec3(0.0);
    vec2 uv0 = uv;

    // Controlled fractal mirroring (less chaotic)
    for(float i=0.0; i<3.0; i++) {
        uv = abs(uv) - 0.4 - (bass * 0.03);
        float angle = u_time * 0.15 + i * 0.8;
        float s = sin(angle), c = cos(angle);
        uv *= mat2(c, -s, s, c);
        
        float d = length(uv) * exp(-length(uv0));
        vec3 col = get_palette(d + i * 0.5 + u_time * 0.2);
        
        // Sharper, more defined shapes instead of raw light
        float ring = abs(sin(d * 15.0 - u_time * 2.0)) / (30.0 + high * 15.0);
        ring = pow(0.005 / ring, 1.1); // Focused line
        final_col += col * ring;
    }
    
    // Better contrast and exposure control
    final_col = final_col / (1.0 + final_col); // Tone mapping
    final_col *= (1.5 + bass * 0.5);
    
    // Vignette to center the view
    final_col *= smoothstep(1.5, 0.2, length(uv0));
    
    fragColor = vec4(final_col, 1.0);
}
"""

# Fire & Ice Shader (Opposing Elements - ENHANCED FBM)
FIREICE_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f*f*(3.0-2.0*f);
    return mix(mix(hash(i), hash(i+vec2(1.0,0.0)), f.x),
               mix(hash(i+vec2(0.0,1.0)), hash(i+vec2(1.0,1.0)), f.x), f.y);
}
float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 4; i++) { v += a * noise(p); p *= 2.0; a *= 0.5; }
    return v;
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    
    float bass = u_audio[1] * 2.5;
    float high = u_audio[45] * 3.0;
    
    float split = sin(u_time * 0.5) * 0.2; // Moving divider
    float dist = uv.x - split;

    // Elemental textures
    float fire_pattern = fbm(uv * 3.0 - vec2(0.0, u_time * 1.5) - bass * 0.1);
    float ice_pattern = fbm(uv * 5.0 + u_time * 0.5 + high * 0.1);

    vec3 col_fire = mix(vec3(1.0, 0.2, 0.0), vec3(1.0, 0.8, 0.0), fire_pattern);
    vec3 col_ice = mix(vec3(0.0, 0.5, 1.0), vec3(0.8, 1.0, 1.0), ice_pattern);
    
    // Apply contrast based on distance from split
    vec3 col = mix(col_fire, col_ice, smoothstep(-0.05, 0.05, dist));
    
    // Divider line
    float line = smoothstep(0.02, 0.0, abs(dist));
    col += vec3(1.0) * line * (bass + high);
    
    // Pulses
    col *= (0.8 + 0.2 * sin(u_time * 4.0 + length(uv) * 10.0));
    
    fragColor = vec4(col, 1.0);
}
"""

# Rainbow Flow Shader (Hyper-Vibrant Psychedelic Silk - OVERHAULED)
RAINBOW_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

// Hyper-vibrant spectrum palette
vec3 get_spectrum(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.0, 0.33, 0.67);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    
    float bass = u_audio[1] * 2.5;
    float mid = u_audio[15] * 2.0;
    float high = u_audio[45] * 3.5;
    float energy = (bass + mid + high) / 3.0;

    // Multi-layered fluid warping
    vec2 p = uv * 2.0 - 1.0;
    p.x *= u_resolution.x / u_resolution.y;
    
    for(float i=1.0; i<8.0; i++) {
        p.x += sin(p.y * i * 0.8 + u_time * 0.5 + bass * 0.2) * 0.3 / i;
        p.y += cos(p.x * i * 0.8 + u_time * 0.4 + mid * 0.2) * 0.3 / i;
    }
    
    // Calculate color based on warped position and audio
    float color_t = length(p) * 0.3 + u_time * 0.2 + energy * 0.1;
    vec3 col = get_spectrum(color_t);
    
    // Add iridescent "silk" highlights
    float silk = sin(p.x * 15.0 + p.y * 10.0 + u_time * 5.0);
    col += get_spectrum(color_t + 0.5) * max(0.0, silk) * 0.4 * (0.5 + high);
    
    // Add 'glitter' shimmer on high frequencies
    float shimmer = fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
    if(shimmer > 0.98 - high * 0.01) {
        col += vec3(1.0) * high * 0.5;
    }
    
    // Contrast and Saturation
    col = pow(col, vec3(0.9)); // Saturation boost
    col *= (0.8 + energy * 0.4); // Brightness scales with energy
    
    fragColor = vec4(col, 1.0);
}
"""

# Geometric Chaos Shader (Exploding Morph-Shapes & 3D Camera - ENHANCED)
CHAOS_FRAGMENT = """
#version 330
uniform float u_time;
uniform vec2 u_resolution;
uniform float u_audio[64];

out vec4 fragColor;

// SDF primitives
float sdSphere(vec3 p, float s) { return length(p) - s; }
float sdBox(vec3 p, vec3 b) {
    vec3 q = abs(p) - b;
    return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0);
}
float sdTorus(vec3 p, vec2 t) {
    vec2 q = vec2(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

mat2 rot2D(float a) { return mat2(cos(a), -sin(a), sin(a), cos(a)); }

vec3 getPalette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.263, 0.416, 0.557);
    return a + b * cos(6.28318 * (c * t + d));
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - u_resolution.xy) / u_resolution.y;
    
    // Multi-band audio extraction
    float bass = u_audio[1] * 2.5;
    float mid = u_audio[15] * 2.0;
    float high = u_audio[45] * 3.5;
    float energy = (bass + mid + high) / 3.0;

    // --- ENHANCED CAMERA MOVEMENTS ---
    // Panning (Left/Right) based on bass
    float pan = sin(u_time * 1.5) * (0.8 + bass * 0.5);
    // Tilting based on mids
    float tilt = cos(u_time * 0.8) * (0.5 + mid * 0.5);
    
    vec3 ro = vec3(pan, tilt, 3.5); // Camera origin moves
    vec3 rd = normalize(vec3(uv, -1.8)); // Ray direction
    
    // Anti-clockwise rotation based on high frequencies
    float rot_v = u_time * 0.5 + (high * 0.2);
    rd.xy *= rot2D(rot_v);
    rd.xz *= rot2D(u_time * 0.3);

    float total_dist = 0.0;
    vec3 col = vec3(0.0);
    
    for(int i=0; i<80; i++) {
        vec3 p = ro + rd * total_dist;
        
        // --- 3D SPACE REPETITION & MORPHING ---
        vec3 p_grid = fract(p + u_time * 0.2) - 0.5;
        
        // Rotate individual objects
        p_grid.xy *= rot2D(u_time + mid);
        p_grid.yz *= rot2D(u_time * 0.7);

        // Calculate morphing between Box, Sphere and Torus
        float d1 = sdBox(p_grid, vec3(0.12 + high * 0.05));
        float d2 = sdSphere(p_grid, 0.15 + bass * 0.05);
        float d3 = sdTorus(p_grid, vec2(0.15, 0.05 + mid * 0.02));
        
        // Morphing factor driven by time and energy
        float m1 = 0.5 + 0.5 * sin(u_time * 2.0);
        float m2 = 0.5 + 0.5 * cos(u_time * 1.5 + energy);
        
        float d = mix(mix(d1, d2, m1), d3, m2);
        
        if(d < 0.001) {
            // Complex lighting and color
            vec3 normal = normalize(p_grid); // Simplified normal
            float diffuse = max(0.0, dot(normal, vec3(1.0, 1.0, 1.0)));
            
            vec3 shapeCol = getPalette(total_dist * 0.1 + u_time * 0.2 + energy * 0.2);
            col = shapeCol * diffuse * (2.0 / (total_dist * 0.5 + 1.0));
            
            // Add neon edges
            col += getPalette(u_time) * pow(0.05 / (d + 0.01), 1.2) * 0.1;
            break;
        }
        
        total_dist += d;
        if(total_dist > 15.0) break;
    }
    
    // Background atmospheric fog/glow
    col += getPalette(u_time * 0.1) * (0.1 + energy * 0.1) * smoothstep(1.5, 0.0, length(uv));
    
    // Final color pop
    col *= 1.2;
    
    fragColor = vec4(col, 1.0);
}
"""

VERTEX_DEFAULT = """
#version 330
in vec3 position;
void main() {
    gl_Position = vec4(position, 1.0);
}
"""
