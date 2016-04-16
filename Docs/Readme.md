# Jarvis: A Simple Idea....
_________

*Jarvis* is intended to be a fully functioning P2P script runner with automatic network consistency and internal host detection.

With big dreams of eventually being able to consider itself a full fledged AI named *Tonishta* (Irish for second in 
command), Jarvis has a long way to go. *Jarvis* intends to evolve from a simple P2P network that automatically loads and 
runs user writeable scripts and uses Text to Speech to respond back to the user, to an AI that can determine its own 
functionality and implement its own internal functions with intelegent interpretation of human speech using the Google
Speech to Text API, or any future implementable Speech to Text AI with open/free source. 

Originally intended to be an experiment to play with *OSx*'s built in Text to Speech capabilities, it slowly evolved into 
its current iteration. The name *Jarvis* takes its inspiration, rather obviously, from Tony Stark's *'Jarvis'*. *Jarvis* 
will eventually inherit its inspirations qualities of becoming an AI capable of becoming a full fledged "right hand man."

### Functionality:
--------

Many of *Jarvis*'s conceived functionality's are still under development. The list of features still under development
includes, but is not limited to:

1. Speech based response.
    This feature is currently implemented within *OSx* environments with use of *Jarvis.Apps.JarvisSpeaker.JarvisSpeaker*, but 
    development has delayed until completion of the P2P network protocol's.
2. User implementable, and automatically loaded Scripts and External Programs API
    This feature is in the conceptual stage of design. Certain aspects of this concept have been implemented with 
    *Jarvis.Resources.Scripts*, but the code contained within this location are all used for core functionality. Currently,
    the developer envisions a system that automatically polls for all runnable code snippets within *Jarvis.API* and then
    publishes that list of scripts to the P2P network, and receives a list of: "What *Jarvis* hosts have what code snippets
    that do what."
3. Complete implementation of a protocol for the P2P network. 
    Jarvis currently does not establish a working, flexible network. It simply searches for new hosts and makes an automatic
    *AF_INET,SOCK_STREAM* connection to perform a handshake.
    - Currently, the developer is still conceptualizing the handshake and protocols to be used by *Jarvis*.
     
Currently implemented features:

1. Automatic host detection and host verification in the background with *Jarvis.Resources.JarvisServer*.
2. External code/software piping and threading with *Jarvis.Resources.osInteraction.Interaction*.
3. Filesystem interaction and symlink creation with *Jarvis.Resources.osInteraction.Linker*.
4. Internal data persistence via Pickle with *Jarvis.Resources.Libraries*. 
    Data persistence stored in *Jarvis.Libs*.
5. *Mac OSx* Text to Speech interaction.
    View above preamble relating to Speech Based Response.