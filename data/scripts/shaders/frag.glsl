#version 330 core

uniform sampler2D canvasTex;
uniform vec2 gameOffset;
uniform float transitionTimer;
uniform int transitionState;
uniform float shakeTimer = -1.0;
uniform float caTimer = -1.0;
uniform float hitTimer = -1.0;

uniform vec4 los[64];
uniform int losType[64];
uniform vec4 circles[4];

in vec2 uvs;
out vec4 f_color;

const float PI = 3.14159265359;
const vec2 gridSize = vec2(64, 64);
const float caCoef = 0.005;
const float shakeCoef = 0.01;

// TODO: get these from config.py and update scale 
const vec2 canvasSize = vec2(512, 288);
const float canvasRatio = canvasSize[1]/canvasSize[0];
const int scale = 3;

vec2 rotateVec(vec2 vec, float theta) {
    return vec.x * vec2(cos(theta), sin(theta))
    + vec.y * vec2(sin(theta), -cos(theta));
}

float linearEase(float x) {
    return -2*abs(x - 0.5) + 1;
}

void main() {
    f_color = vec4(texture(canvasTex, uvs).rgb, 1.0);
    float centerDist = distance(uvs, vec2(0.5, 0.5));

    // vec2 uvsPx = vec2(
    //     floor(uvs.x * canvasSize.x / scale) * scale / canvasSize.x,
    //     floor(uvs.y * canvasSize.y / scale) * scale / canvasSize.y
    // );

    // TODO: Understand why this works
    vec2 uvsPx = vec2(
        floor(uvs.x * canvasSize.x) / canvasSize.x,
        floor(uvs.y * canvasSize.y) / canvasSize.y
    );

    vec2 offsetPxUvs = vec2(uvsPx.x, uvsPx.y) - gameOffset;

    // Circles
    for (int i = 0; i < circles.length(); i++) {
        if (circles[i][3] == -1) {
            break;
        }
        else {
            vec2 center = vec2(circles[i].xy);

            float d = distance(vec2(offsetPxUvs.x, offsetPxUvs.y*canvasRatio), vec2(center.x, center.y*canvasRatio));
            if (d < circles[i][2] && d > 0.07) {
                // float intensity = (d - 0.07) / circles[i][2];
                // if (x > 1) {
                //     x = 1;
                // }

                float shine = 0.6+0.4*(pow(abs(sin(uvsPx.y*20+uvsPx.x*10)*cos(uvsPx.y*15)), 5));
                // float shine = 0.8+0.4*(pow(abs(sin(uvsPx.y*20+uvsPx.x*10)*cos(uvsPx.y*15)), 5));

                // if (f_color.x+f_color.y < 0.3) {
                //     f_color = vec4(0.5,0.5, 0.5, 0);
                // }
                // else {
                f_color = mix(f_color, vec4(pow(1.5*shine, 1.5), 1.3*shine, 2.2*shine, 0), 0.5*shine);
                // }

                if (shine > 0.75 && shine < 0.8) {
                    // f_color = mix(f_color, vec4(0.5, 1, 1, 0), shine);
                    f_color = mix(f_color, vec4(0.8, 0.8, 1, 0), shine);
                }
                
            }
        }
    }

    // Line of sights
    for (int i = 0; i < los.length(); i++) {
        int type = losType[i];

        // dummy value
        if (type == -1) {
            break;
        }

        vec2 losPos = vec2(los[i].xy);
        
        float angle1;
        float angle2;

        if (los[i][3] == -1) {
            angle1 = -1;
            angle2 = -1;
        }
        else {
            angle1 = 2*PI-(los[i][3] / 180 * PI);
            angle2 = 2*PI-(los[i][2] / 180 * PI);
        }


        losPos += gameOffset;
        vec4 color;
        vec2 delta = -losPos + uvsPx;
        delta.y *= canvasSize.y/canvasSize.x;
        float mixIntensity = 0.3-length(delta)*3;

        // mixIntensity = round(mixIntensity*30)/30;
        mixIntensity = mixIntensity;

        // see player
        if (type == 0) {
            color = vec4(1, 0.5, 1-mixIntensity*2, 0);
        }

        else if (type == 1) {
            // color = vec4(0.2, 1, mixIntensity*2, 0);
            color = vec4(1-mixIntensity, 1, 1, 0);
        }



        float angle = PI + atan(delta.y, -delta.x);
        // f_color = mix(f_color, vec4(angle / 2 / PI, 0, 0, 0), 0.5);
        // f_color = mix(f_color, vec4(angle2 / 2 / PI, 0, 0, 0), 0.5);

        // TODO: Make this less redundant
        if (mixIntensity > 0 && length(delta) > 0.025) {

            // if (mod(int(uvs.x * 200), 2) == 0 || mod(int(uvs.y * 200 * canvasSize.y/canvasSize.x), 2) == 0) {
            if (mod(int(uvs.y * 200 * canvasSize.y/canvasSize.x), 2) == 0) {
                color *= 0.8;
            };


            // color *= 1+noise1(uvs.x);



            // Full circle
            if (angle1 == -1) {
                f_color = mix(f_color, color, mixIntensity);
                // f_color = mix(f_color, vec4(1, 1, 1, 0), 0.9);
            }

            else {
                if (angle1 > angle2) {
                    if ((angle > angle1) || (angle < angle2)) {
                        f_color = mix(f_color, color, mixIntensity);
                    }
                }

                else {
                    if ((angle > angle1 && angle < angle2)) {
                        f_color = mix(f_color, color, mixIntensity);
                    }
                }
            }
        }





    }

    // Blurry shake
    if (shakeTimer >= 0) {
        float shakeIntensity = (1 - shakeTimer)*centerDist * shakeCoef;
        vec2 shakeSampleVec = vec2(0.0, shakeIntensity);
        vec4 caSample1 = texture(canvasTex, uvs + shakeSampleVec);
        vec4 caSample2 = texture(canvasTex, uvs - rotateVec(shakeSampleVec, 2.0*PI/3.0));
        vec4 caSample3 = texture(canvasTex, uvs - rotateVec(shakeSampleVec, 4.0*PI/3.0));
        vec4 sampleMix = mix( mix(caSample1, caSample2, 0.5), caSample3, 0.5 );
        f_color = mix(f_color, sampleMix, 0.5);
    }

    // Chromatic abberation
    if (caTimer >= 0.0) {
        float caIntensity = (1.0 - caTimer)*centerDist * caCoef;
        vec2 sampleVec = vec2(0.0, caIntensity);
        float caSample1 = texture(canvasTex, uvs + sampleVec).r;
        float caSample2 = texture(canvasTex, uvs - rotateVec(sampleVec, 2.0*PI/3.0)).g;
        float caSample3 = texture(canvasTex, uvs - rotateVec(sampleVec, 4.0*PI/3.0)).b;
        f_color.r = caSample1;
        f_color.g = caSample2;
        f_color.b = caSample3;
    }

    /*
    0  No transition
    1  Starting transition
    -1 Ending transition
    */
    if (transitionState != 0) { 
        float tTimer = transitionTimer;
        if (transitionState == 1) {
            tTimer = 1.0 - transitionTimer;
        }
        f_color.r *= clamp(tTimer, 0, 1);
        f_color.g *= clamp(1.5*tTimer, 0, 1);
        f_color.b *= clamp(2*tTimer, 0, 1);
        // f_color *= tTimer;
        // f_color.rb *= tTimer;

    }

    // f_color = mix(f_color, vec4(0), pow(centerDist*1.2, 1));
    if (hitTimer != -1) {
        f_color = mix(f_color, vec4(0, 0, 0, 0), 0.5*pow(1-hitTimer, 2));
    }
    // f_color = mix(f_color, vec4(), 0.9999);

}

