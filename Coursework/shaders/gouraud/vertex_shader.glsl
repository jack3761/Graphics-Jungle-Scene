#version 130		// required to use OpenGL core standard

//=== in attributes are read from the vertex array, one row per instance of the shader
in vec3 position;	// the position attribute contains the vertex position
in vec3 normal;		// store the vertex normal
in vec3 color; 		// store the vertex colour

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragment_color;  // the output of the shader will be the colour of the vertex

//=== uniforms
uniform mat4 PVM; 	// the Perspective-View-Model matrix is received as a Uniform
uniform mat4 VM; 	// the View-Model matrix is received as a Uniform
uniform mat3 VMiT;  // The inverse-transpose of the view model matrix, used for normals
uniform int mode;	// the rendering mode (better to code different shaders!)

// material uniforms
uniform vec3 Ka;    // ambient reflection properties of the material
uniform vec3 Kd;    // diffuse reflection propoerties of the material
uniform vec3 Ks;    // specular properties of the material
uniform float Ns;   // specular exponent

// light source
uniform vec3 light; // light position in view space
uniform vec3 Ia;    // ambient light properties
uniform vec3 Id;    // diffuse properties of the light source
uniform vec3 Is;    // specular properties of the light source


void main() {
    // 1. first, we transform the position using PVM matrix.
    // note that gl_Position is a standard output of the
    // vertex shader.
    gl_Position = PVM * vec4(position, 1.0f);

    // 2. calculate vectors used for shading calculations
    // WS6
    vec3 position_view_space = vec3(VM*vec4(position,1.0f));
    vec3 normal_view_space = normalize(VMiT*normal);
    vec3 camera_direction = -normalize(position_view_space);
    vec3 light_direction = normalize(light-position_view_space);

    // 3. now we calculate light components
    // WS6
    vec3 ambient = Ia*Ka;
    vec3 diffuse = Id*Kd*max(0.0f,dot(light_direction, normal_view_space));
    vec3 specular = Is*Ks*pow(max(0.0f, dot(reflect(light_direction, normal_view_space), -camera_direction)), Ns);

    // 4. we calculate the attenuation function
    // in this formula, dist should be the distance between the surface and the light
    // WS6
    float dist = length(light - position_view_space);
    float attenuation =  min(1.0/(dist*dist*0.005) + 1.0/(dist*0.05), 1.0);

    // 5. Finally, we combine the shading components
    fragment_color = ambient + attenuation*(diffuse + specular);
}
