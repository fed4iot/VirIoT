package xacmleditor;

import java.awt.*;


/**
 * This is an implemenation the LayoutManager Interface. It is necesary
 * since we want put the componets in whereever place of its domain.
 * @author Alberto Jiménez Lázaro y Pablo Galera Morcillo
 * @version 1.3
 */
public class MiLayout implements LayoutManager {

    // Constructor
    public MiLayout() {
        }


    // Método para la incorporación de componentes
    public void addLayoutComponent( String name,Component comp ) {
        }

    // Método para eliminar componentes del controlador
    public void removeLayoutComponent( Component comp ) {
        }


    // Fija la dimensión del controaldor en función de la dimensión
    // de los componentes y su posición, para que se vean todos en
    // el espacio de pantalla destinado al controlador
    public Dimension preferredLayoutSize( Container parent ) {
        Insets insets = parent.getInsets();
        int numero = parent.getComponentCount();
        int ancho = 0;
        int alto = 0;

        for( int i=0; i < numero; i++ )
            {
            Component comp = parent.getComponent( i );
            Dimension d = comp.getPreferredSize();
            Point p = comp.getLocation();

            if( ( p.x + d.width ) > ancho )
                ancho = p.x + d.width;
            if( ( p.y + d.height ) > alto )
                alto = p.y + d.height;
            }

        return( new Dimension( insets.left + insets.right + ancho,
            insets.top + insets.bottom + alto ) );
        }


    // Controlamos la dimensión mínima que debe tener el controlador
    public Dimension minimumLayoutSize( Container parent ) {
        Insets insets = parent.getInsets();
        int numero = parent.getComponentCount();
        int ancho = 0;
        int alto = 0;

        for( int i=0; i < numero; i++ )
            {
            Component comp = parent.getComponent( i );
            Dimension d = comp.getPreferredSize();
            Point p = comp.getLocation();

            if( ( p.x + d.width ) > ancho )
                ancho = p.x + d.width;
            if( ( p.y + d.height ) > alto )
                alto = p.y + d.height;
            }

        return( new Dimension( insets.left + insets.right + ancho,
            insets.top + insets.bottom + alto ) );
        }



    // Reescala los componentes a su tamaño preferido en caso de que
    // se pueda hacer
    public void layoutContainer( Container parent ) {
        int numero = parent.getComponentCount();

        for( int i=0; i < numero; i++ )
            {
            Component comp = parent.getComponent( i );
            Dimension d = comp.getPreferredSize();

            comp.setSize(d.width,d.height );
            }
        }
    }

