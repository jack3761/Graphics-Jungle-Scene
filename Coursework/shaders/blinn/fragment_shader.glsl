# version 130 // required to use OpenGL core standard

//=== 'in' attributes are passed on from the vertex shader's 'out' attributes, and interpolated for each fragment
in vec3 fragment_color;        // the fragment colour
in vec3 position_view_space;   // the position in view coordinates of this fragment
in vec3 normal_view_space;     // the normal in view coordinates to this fragment


//=== 'out' attributes are the output image, usually only one for the colour of each pixel
out vec3 final_color;

//=== uniforms
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


///=== main shader code
void main() {
    // 1. calculate vectors used for shading calculations
    // TODO WS7
    vec3 camera_direction = -normalize(position_view_space);
    vec3 light_direction = normalize(light-position_view_space);
    vec3 halfway = normalize(light_direction+camera_direction); //TODO WS7

    // 2. now we calculate light components
    // TODO WS7
    vec3 ambient = Ia*Ka;
    vec3 diffuse = Id*Kd*max(0.0f,dot(light_direction, normal_view_space));

    // the Blinn-Phong specularity is straight from lecture notes
    // note the scaling of the specularity index Ns to ensure specularities
    // consistent with Phong. 
    vec3 specular = Is*Ks*pow(max(0.0f, dot(halfway, normal_view_space)), 4*Ns); //TODO WS7 

    // 3. we calculate the attenuation function
    // in this formula, dist should be the distance between the surface and the light
    float dist = length(light - position_view_space);
    float attenuation =  min(1.0/(dist*dist*0.005) + 1.0/(dist*0.05), 1.0);

    // 4. Finally, we combine the shading components
    final_color = ambient + attenuation*(diffuse + specular);
}
