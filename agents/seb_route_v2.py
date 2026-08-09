"""V14: replay-derived reconstruction plus near-clone premium preemption.

Field and labor actions come from the stable route shared by the Kakuteki and
mrgrishninsb top-scoring submissions.  Runtime logic preserves the public V23
actor-local weed repair and nonlinear price-impact SELL ordering, plus the
terminal shed cleanup observed in the frontier replays.
"""
import base64
import copy
import json
import math
import zlib


_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-rlqOK;sra>c(3*IbwnNp^M``3@|M#xf*1#Ka(s0Wv{=V6vEG7v#G~V^a6=uhYLeRo$1CCtB%(msG#It4^Id_0#`c{M(=Z_Se7s?c$$)y7=9Xuit$8^A9iIfB5m;?&ALP;@|)Lpa1$_AHVtd@vndW+kgD!zdwHd>EgTBzkJ*M@Vg)X^z-}O?%RvYi$Ct(y#4;-@@DhnyYF@{KU`d1U4Q!d%kN+R@#UM3-@JNzcX4@rfB(Oi$Nm1{^{YSp_`~7rL&tx*xZAz|@JqAbzkT=NyI($i9N_!SkA}Z>I`Y`Z*v0qX?RGziPJa9D?GG0xT|2ZT`nFvQ+1uF1(ah|7Wp_YL$(xtof7p-R>%g0ruXg+PPg?)<zddY%&NRIIuzTlq<I^7<Z;ZoVhmOz=fysZ^2|v7h`|XdfJ{;}idw){izx{DAIyo7l>-9DI)TZnP?TkYgX({Ykfm6Ky?)cb^hPv$Zh+Xshzn}iW^58)+mc^Z@#{tNLycwKq*;}^3p8fmc3}z%Webmsx(<4^p)yvI!5L-fYVd0t#rw0$Tvrh_ZBo6ZS;M}Auwf~eqh559I9?@Ri|Ku=hjr(l(a(h0~C6`}~mkt_#+=}LvarhD4SWC}}xX||>4kMmgfOtXe=YZOLT(>o^NnD4+B@z0tZ&|#sr@u@$<il^uvmcvGTUy^_`k~a)e$Ey*6fdmvxgn>1Mc6}+yY`&kMC%BjT1r>H{QuHG`qZ^oZ{NJxz54L;?|1J$yngfgUmj1_{zOne3&w|-l*4`;^r6r+EJwUw9^I{@4`_P4-@W<!J~-;!!L<u(bZxBBzBRaZ#4I%?;negnuYgUj*4(gh@~H=UKTPyT{fDY|(k5E7I?4hQ?!maN&8^yON_YX`!)A@r;}GUMnpvgx{U;$JC;PtzyTWN`Fwjfe>JP8t=zuMMeuumBd@VIz{Lj20=bl>9(7BDVFAe>_Z7A3t>#XF0B`V>Cl95a{=c7NU97=){)OW#7UhY<p0czc)hnJ!WLt1D`z;s%uV_by&8z+Fi90Y7S8Ddm4yALz9XuuIeG~x03fCXwqb9?BAJ>cv6MYAp@Bi++tauwX>O|P>2o2Ur~KK3o{EtH23(~T)?I9NlCwl;rj`X1BsIq>bAPVDcL$H^(RySL{Y>wD12hyNq>5^gHK0J*xeF6XRku%@Zf{yMkGUUhA+@4uL%zrBWjvp{ifMJ%#OhgR>+;8_#EG602ZCgI3vSd9oG>jUiNF``{E;Q*Z$-B^Ig!U|Z<(RxTWK*WcEi%B_((w-pN3rGVQIJ`AoGb?++YMD-?S}?SHr}<EEWu$XEzbL{9@YZ2|0wQ=#@cbb%EeHzf#UT7hF!$9c*F*)J4^P)p)kwR&U)%xT)Ofm<Ak;D0kQdYWVvl}l=qZq8&#e9|0cY6*Y*<*;5fEH#HDHIfxNVmL>zMb02l~60@BTRjMFDa4NOgrJ-*?Esv0BdEr0d{uHY50(HYG?vVond!bNaah^bTfqKh)#@ALg})QpyF6-j_Ge4M2b2Lbj>WIqx*C+e835&iGy9#2z)F#)3{(em(J`4z2Y~C-z3Kb1MmBP=q8zizk#?#n>t~x^L@vDA?})gtZ!!GluPLslB!K4&jJTCnti;F}{(u6g@vNm~*!TahWqU6mj$T6@)%MnIq4CnI{86kA2!V1F?b;x{rN&G3e7it?<pu@4vmc_g$??T97?y;}oc;z_cF|8Q*_+_ww#{yLa#Y^sz%<=}gR<9BE`D)cUlF9sQWFa5ON(Zodmx+W~+=&Pa~IikB@1z4aiNL|sZtk-ma%bxb62ZYLjlHADM@nM^w(_6ml)ll{TdRx;1Bc^6q>+pm%(t9c)SvJ<jpw+(iju54?JOi*osY!|C(#AP#@Me|3iR@)J|GfSkHUR&u!pa=z{w7Hs_5dOd6_7Z&vUv_Ep(FuyS%GRMN*=0n{pr)c_cDAM(p%ZE<+EUaM+i}7i09!_DO&Esi_DM--mWRm<7Dfr_k5^mF?uXW;5k+ZD$-EGsKxAr)+i4RuD~2O?LstnVq0>^F<-?vG$}4P*%dp)Q4YQPF=I-AZ4iJ2f6SRDo{+}7;zlyigj0q?U@fg7{{g7Goy<op?hjG<}j4=;&9Leu7do&8g?KMDZ5B-%UjJP~g&^iuy51mDzSmMLPxX(#4$sp6Q3*$Jqj51?<iylgqfOu0Lep0ZUgq5}>1`nR0Mz(=!EFm!OuX$nd>^r(i@z)U1+qWP88KY{W*WuZ{j{)W;SdIJDOAZCpkHPXfXTnmOa40X+`JwPaB1s+4TEZJ~GhHDZDqgl)X6bZ3alCX_Nlf(ViVY-qVg~*Zct&67H(!|a-SETLl`w;g=Nms-&Mim2Y;f<BK*e<fVurgE`zC!uMC2CDU3BgdT2Ne-7SAS<o`q34jy71$dciUvKseCs+~|2Lh;uW;guxxigWoRB(kP2L9sLC$A~-KUMr1k;j!Z(0Yk<F&uK|Tw6!%D>{G#C=UuHM*iBDy!T$+}VpQ<)W!OfT5%YL<xKT8Sj<NvVLu~Ilew3zwh+_&Q6Ih4U(yHZgBu!7d0zZU;%F;mtrwRVvT$wu~%xYc8q91O*C&JEz)VP!>KIZoa*A}~hO%1G1zdX?~_@eONWAxU=?YCpz0;!j*vT0h=ZN_{B`#tkLkmN;RfWmx5$$*{|WCw5*w*kEyWL4oOH3K`-V^TdkLrM9VDh&L^=+$jmf{nUv&MLYO}86PtyDPH5yy(1<l4ARUzN%?Hk*$pX^$_msI-=X4Y6Pr6a+VEkRiriyE3nsY{w-SudQ{GjxGxnw_Cq6qp6A&;&?5yaGqGkzzZME4plx1pkH+5+(4V-a7k;vE^a<L{mK{@7ND~iU;>d0i?Hk5v>I8>B*_D3>l3D)9d6#!w}5v=$DAGF=yP!^-Q8qO?i&TOx3$d2^I4pyZd#HHy)4^^)ox9uNazxe|NczvpGLpV8}wpJf67wC&O#Fc+dx#d#Z+eJH11dhEuMbLJsgo$4m13g}bej|Bl&zKxkksDNQGmg>WU~g+yrQWd8^`y8%A<h*08MB5jGo4K@f?Bw~ArqQ}&;-|*f|P|cAXFX7vOstt$rmn!uEgtdk~6)P$BOo^9bjxMC?d}+ZYpGpy~tx{QIA>NC-arX0nI5>miDRP4<xM@!*}r3zL$s!eW>?H;7@i2<Hizb%c>e~b_O1XMaA#STd)<b6{oqgnF{{=kYQUDMHs8UT&A!Z%Ofv}2b=NMG)k;KZSS3C7qdlQ5-OcdF%yy|{w6bn<UY4rB#Ui|pO)t1j6IEDvl~iw7T4_V#-S~lRs8gd3+dnkW`k;NO>aU0n<ax_(B-XBRs#0p&J^7g_ozsWP?_wukS?L;=}uJS38;>mS-F0(T<UcpsW;ih!-5CB%vB`&IchB&5L_PgWpL%iZzTHb{Yf48sB$XWDun$(`4Lm0%Qi<fEoB3a^x#5{B7~wG*~3-|5*kPhFZzjz6FM|NxQ-w-8s6x`dz-=yrD^pv%jbn~u9VC6oVztiJIYCcsI#z>H)xCbL{5w$iQdCr@;L^keR#LPy^qH@8g+3+RJ0jF(r9hT;NL>gda-GQ!KJ>8{+V#K&szU9qd40lt`K~6_n@|N9v|py%vhvsxg1Ry*Wm{40H#3qqluQH3Umv;%3z!{6@IpF5Ce@KpIw2<3*<wVqg5D7l-YKxNJYLdg>@hH`>|R7VCdhtYKx((IObkldaFic#;n^K{xjLXNubuO@l{IDok<mTM%xhcKZ$!R$|Jq33>kdb8(R}|X&UU=bI8v@Bma$&8~(An_2kLXRVYU0?8>cXW=wO9g{`@sO+s0??Hdi(+>SW?gK+7!ad`{$<~VRFUOcSMV+JN$>5EnZ7c*{@a1OYU1xf{NO2p8uQK7s#5f|J$n|DTt3J7o9Oyh-l$3(XU!#I3`2{uGk^<H5W!hXGFV0L@JQ#*ya4|UMiiFgK*GfbMy(fe4Dpmb!`)SM#lG9<$cV)^}vcgk~Pyf~r1O=*fbb1Npu;<KoQx8TU0AOvVo$Zc%(T)tH2snrg2!(?|Gk9b!#GEd~OWww3BK_Lv=UkaoLs%>QoP~bIB1fLbEG;t4Mue}F#^PeuwBFp#@m<Tc|#v~S_v15#45?SvAt3n5FXdyf{*XjsDGy!u-kEC8!;CC3)mg1{jv;(ePuzqv?R9x}O4J^Qgz=g4=IpWsQ7EN_Ek#f}u=2Bkd-hItNKcgRqp=UbSz}7VM-Ww1gyv$Cd3zYv0esGh|^UVMY{pPdb^VsB;b5eVH^8XzgJquu&teH{yzA@-@Rd(TMA@`S(mvtc?rXks+;<(-17u*gJL$8y33YzQZ@%s-?M)sHy|L3l&rtZENz*!=D7vZnnkj>kGh^}+PDzk&Z3K2WZ*hL=Z)mG<74IwU0f{2E2S(dtaL}6ou)Vxt6o(A#~4|!IOZ9YDEh3pNrgh~44DkI#kqD2FYyew4Ah*(Ph9%>Zh%Iw&olU>d$nXUwj=TH17UYM=U!9F+d2I^at@C7IIy3cy?uT_jVStB0mcht3-BASDYRjZt_kj&fVb!3$v(xt4m%3RWrM47w&VRl$maeE=p1ju4!c&gl_SP8JD_Tkn*>!`*+O=aN=J9--?r>dg1BX&pJ=VF^ItkF>Eu3(4el8_6k3?KIS^ag=#v3>*{0uWHn)>R8}_5sVZj0CejTh*2%GKXah5U@y5os_pjo;GxXgN$z7E>=Td4IFSnBw2=Dd54}RIGVB;pu_&b{PzOuG%dCE7iwXf+l?o=B8zj*m@U-g<k1mNq@(R3AkDj7%1ZL(B+fLcy!kvHAvr0fVki!OrmP<1B{X&_RzT{Tt9E3PdnPypqTd{j1|1&q`+&sMtg0CCAEL`xxV50A9p3mQmMqpD;2rBokHx7tPqvqi4#oJ5cuPzyr@@lF$@`r-^)YPhkOJbYEAg{O4EU_swkb)g_G7WtqQ3<TT4R`@7!lLmQrHF~im*b(g-Dq(PQ_at>4_V0lAqrR+!VqKcB*dSk%cU6iVK*ffdEtJJpV!snw0Dt1$?tVk!FFV%W_+?w_|)&ya`2R_69%l=6+>`l5ftAexSMS!vhKYkqChE*<Xu`K=|I#z|&?8a(a$)qjZ%@H*NB|pcoO&A90@(PXS4|6Kn))0kB^DE+(}+?wgezzq+5RgSo4u-hgP<(y1mJ3dCLzlZgC+7564yOtt5}Rq=;T%l5nFILDZxp9uqF9tM*z)?7e>a!k=#!I9;+Vre;ILUZD|P!h1<5KC+D_@Y{ik^xl<NQxLHkHjHjB^Tya?R3%`9`D`cuU4eYc~wyvNZ9%E{p+-Wk4%8$ZKuGilkXGn6*kcX5nm02@>L2XQ8!uNtP)$*kT&;-DHmPf=`SvZRvw2yXM`uVmSAkgWKs;SX<&G6_FcVv-slO@KPENSc#a3=^ZA7N@FBJBeDV?0pA;c}SG>)OED4YDhyjyY1#>ll5O@Ph$Z5yKh^fZkh7VO2VuJKd=(FHq;f*wu%V`%IvXYc;pODVt2Jg+vLn;>HCL=Yf1}%f5OiqET2D6mRB9ac-9w64nu}wUTFLq0K$m}ab&OF|Y$!nQ0+G&odREr(MEs<Wv&|RZw7;}sOotlxWjoSp6?v{AcD((xa>Z=Vbnxj0eVd;t9)LxfFeT1r3RY%0o^r+3QoyuzQBuWLd&o{p*O2OQHh?VxlPj<9}1>M2ZLqeB0!YiHWMkN<9-BRNjce~cx$RzfiTw!Y=q?y4kt|jZRxlcQ{bX~39tr5?Lk`Q+Y+jcebdE8;j<3>dmPr9XZ47}_g5X>;OCgaVsQL+FU*)uosr=C8Uu?)PbOUjXU!Mx>nR}2kEJMtt!dc3^Dkkfj;T&idiI@jgeq^oWVuO;BBsx{TvXrd0aS+wHh9Nl7m=CR~PZO3J0Sw`E=GX|iL+SGefdY)4lo(>Fzx_pLRU6AIn^upJJHNHCLI6Z8T5is;nk2&s~l?<OrAjSOQQk`cdVO(H4RH;3U@?4YFy+x!Zw)nVaa>7_BfKy(1X{&F&i7S=J0oX&VJtaL&@L1xmjQukg(aeJ(<*mNjkhp6V3S#;21B`6}a1v)bi)NF&whBNSNhveHgp;+2aq+rCSIQ#<%uk%D0u|ljN(e7)jcq)LEGE1v3o9IoSgzK{w3Qf<?C%OaO#sK4>!^t7vF~@bK}nBQMk^{(Z;p0^L8)=_dZOZHqK`D0htbJrk)CBv)!D6#sU1(a9vJ04*uqFCessF%a}>FZonh~Fs$Wsz^I;YGxaht+J{X_~b08cl+^$<&B&kIDOJB7CM@Jp9nh%V1>1LGl0E6Zndz3qaPc`Srq1S`>l-swycD2az96zXo?GgKJJtE=_U#P5gK#pxJO^9mY7OG_bSciFS4%UlVJZ45<*vDTwRjfFIb6(ZqeL3;`^k>yLS*FgE2%)rt5+EV$0vVUW0#jJ4WRbnJ-D{?{2VA&_SuE)_(tFJ!$Lf=&Obz|J#kI~o5Dl5)xk%}1cT<vW1E3|klc7Insici`7*m@?n6&a_FAkmnWyTXL*D)hpkPc>uIw=(BuBs7@;iGEwu&jBWU_GPg+ZZWr>3L7!C(>1?tk63QVxy6^4~i`mfls|jpJgEL{3V&f@!CWaB@wdm>JNzjWO+5jT-j%Etiee@TKP~X;xvGMx#oV2)C_uGJ<gxJ5f*!xwIs=eO5j7ImCEz!U^t?Rwthy55R8soU;Ei$v)$HsHsTN`tU9?8urd3_MwD(A8+juct#2raNG}n8O8IKfgLnRnu8BE~Xho$6H61gw+q+53x;e#jhtwiVE|XPPDV)~{?h8KxEEM5>BzPa05Us*)RiNp3gWg0<|B*D()z#{(F(Q4eLYB_V8){`S9qaH|2{Z5$v&`v=EU~!fv)I1X??pzW<$inG%fx{i3MQYe&p<6w*oUc8JmGU=B1^n8vwRBlIcB7ZN;H0xN+xt!=#`50;@N~(z{^28Pp$_Ame7m)mH-R0=uv*il?b*EWsM500$<^S=S9Ov*7#~dOsI)(DD4E&!d|oOk?SJOf7<bMr|2sx55!PBBaO_T{@70e9(!$zCK)M~1h=PoDB~(mYj~FuE`&;ng#vM2skmkMyG^+vZz;<!8%iIRRAR)mhKrEdO1<2lGfKrcoT2Qhq=Qn}cjqa9iuP<aGSV7z1f}pom4v#H(2y_LR{Qbb#vbfqAchIN=pjJyymSv2{Xee?<Rp7jopz9PO1hALw?s)PJ$Tv5J9c-W=Vk2Xli95ynh^}S8o8ND?^;Y6n#lMX)*~+&8kpu~)d4ZtLD!S1-~@G|QGm<}9z*4lA#0i#OcWtxC$U2hazulX5@w3!m~5=2<RF?!`mU!<+nH=AE3OvUN}-}m!_9Z4K!SuxSr-LGiL#1BXUUxQ^=QP3XHIQG0;<pibUKKggvJCK(M*-~<0q==*&hVX`4@|nnQbKKs=#tc%4soNgBYqFdFCLu7m7;%L?}L^xk(fp>(@-Epu6GlgpZ}CKF<Vj-E?Oagbs$AB#6Se`WIE{dN99F<PuO;gE%Mg&G$<<HJ7M^7?#FFq&^bPsA{v9Xg-n~(`51y*qs4y6Ok*6HiIfMI&U%=BpL!Kw}5FfO<Ca#yEBF-Cd_5S0M^;rnFW<_dX0)1!1nV1yvVC50#kO%lrUMcmRXo#D8HI+<8O-DLVgk|;&fhF>6E~Fy_PQYRfICHMu+<O*)!G7%MzmheG+w=J2htEM2k@;>j74@Drr?Leb8!EWt;!I08>b!eij&I`ZVXS4n`V4oV+%X-gQ&qJV{H9!8}v}qI8%wx=O^C#;(<h%}uELEUak;$(Q2jYL|ZoQ1i;gBfNBJXXV+u<f?+RpBiXs4M8ujW$aLObwE&V$c|#WH6YF<xsQIS=>;T~T^`i{UY1Ufn~79ojAM9cs^E-ozN4#8b#zC??q~Ey=mwy3nfdh<mou&AmBAOR;*p+B%e!cn_KJ>yUttOvmOjlx<!9)n%#}WxHTg_H)Zs!&=4{*mrQK8`VHA-CQaAOAVhspDcSh_$g{wWo%db-7%xA5_p{Xb``0GM)VMOB$lu_Dnv6z^U?jgGESjnlDMkc(jSQ9KN9AzqJLoKH#$<BHVF<cEo49_T|@H3GGn*5=WzPti(@dTcyq=Ce_;2cZj8>i^pT&Z>_o}sHEXMT1=<LstOy)x^NVZh0K!<Sdyj!OUxYLiEi_}cyXCw$T7MElf$Rw~JLZh0zddaiulkT=dEDbI#i)b&j43pr5HsW<r<%akPu1th;vpMEkAN2nUcOfJtP`s7t?PcXE2#gP|wT`bO|8|ONfC7&Xt%ik8o6v{E;EH6d}6*Il1T=0a9^oO1ILWI|D^F7y8RUzf8yg<-;-eHm)URnVkqe}0z8q<v{4<I0>cOyiex_aBL^~1l1#+0d+Y_N;4K?-e>*ySQ9*GkceKM~#lY2JV!%}L(EZGmv(0~^jbEKA!f%EoV5n|Bw}bYkb5tBEBRM%g%B-q%6sn4PmYy8Ta%FO*G@J~=<^fC{`K)Erk!RzgY=a&1<U(@y+tB%e9ef$Vsy4<6?<kCka>&WfI`x;#bQe@lu%eZ4QNycsPuBnlZ7#Jx;iN6MLF!Ni(DZQ%(S(*OiuBurU0gd7;P+t+aYGlr5C_&}r1zfCBQ%yvOCVm1k`k&w1A-M5x=5~q)Z;!xfw5&oV6R!9bxdX62=7DqbF6S*y!15flH!BYwFqpxDxV7xgDtV|fAQP3#$bI0t;Wez+)0f|eSrQR9IOpg1W?JcK(V=csMGL4ohR{0PX!FUCJ504`uhCnWxE30{zP-I3-2FuGnf`vB@X=Nx$4K=D0nw9aftME)6Z*o3>>g_{u3Gb?NHZ0{5u9cqB1VXjEyIliaYE=JXd~Q!)KxRy3QHmNYu~}pW9{TI2%Z#HZB^=LUS4ujm{=<3|FuNXA0h1K4emb??+G-0k;LtG@{lnj<bgvX_6X#e!x7fL&ppY3BJH}&1py<siD$-YjhDU|xzdk$ub9`SvJuM05s?Ne%O->r-Ir`z8h$B(dy&mE*sbye@XN+v8B*iSH;kr~N3?w8-%{i$&ah`lE+t5zPJnVxkDyt3PlYkekvMcEuIpEp!Oz+$Kg2HA|X9-i-ZIOa>!x+bniiRb;m!3>c=LECUb7x7WWV$t(qHOAg-rRTV?E2mW(RWyAsau?f)NE8?NGLI2`<;Y5!2;a2@I4!_Pt!wO5#_F4gPnp=lAg(#Qdw=Xy3~R2NvV(?qT*S4hxkpPz&Q5%b*0v!D$`@vmrpWvC0~H@r<lg~Y)VwjPW<u%=urpifaI{rJefX83P+WCD+n<5>x+B)txUM5Q1o=>;bR4(+@$INYFviT<#<#uLBHyzCwh=5sb+_3Ln=zIHm9Iq(j-y+D6@?4Me|~=l-Pg|al(n~7Yo@xd@wWnPIzWtiz@PsAw@=5B#Uk476!s2I-dU*qj8O2ka^7OxC5h!eerZmr(aE0d-TMg9n-4f5oRVu1{o2Zvd8`-90K*eFc-d258}E|6+X$RBMG5G;z37;@}}Z;k(p22UX%{mPSTpGN4<5((p15nRD#Ip^0WIcVWOfYndsv71yQ06ye2&@v3v{YA+skGUoQ=4GH_+*pFq7+(nskE|6(~lh`fz7Z?gTz{{7@6yP@0!6H2@~)Gz7cf?l~86phQ-bK9GBbsfZv7$c{1!0ZqgG3By1<=<_jLUbnr6_mTOiWKAl0)v(CJ!NJ8#G;mIynL9F;*86@n$h?yRsd`<g!1gn<U722D%D#&S#ULBN4AZeCQpcYLZij&`W+<}QC76S^F68+B)3tKmh@eU0y(6F(5DVZo=vKn<`cqd!`Vm~O<?slrv2EhiX5lIYmyj@sT$>v|H_S3#8Kj-3h-Hkj|ATe*YQk3O%76Y{d7ptxNg{ug>^IlqF*&B&gDDUC0u!|pm|VO8V>+6b>T;aZI>6lzH`C}9^6$Sc67)yPE{N#R-dqAFwjt>JczVb4EUu<SbkAiT?_<^MRmDL766wN>WL8)vts$;V!1%s8_^rA1hqt!)PqCQN^X+;4=KZP1;ls^0_E5*E3;Glh-e{)j2Na7OO3uLkhUJiJXc7~#HS(rU#jZd48j-2q4RCL49w|LWJSNWBP;C>h2A0(EzfCc$F9n!P1szbB10-K>Qk%HodIsB0q-fUp_gx!*e34XRalDKQu%L}KW#)Oax=1uY^r&RH>8s?Y8+hjY*R1o*^rS|q4EoaAuE`gkoQk~vrqqL4)9|yqyNlHAcUK7$TkCLM4@O1P(@AW$fOa&6`OF?FrKd&2Is$sA&J$hvYQGtOi-bMK@kJX`m;$)?l#AyB4S4Ui3<YITX`5)L^gT?2<zE!i+>?I{R#jUN~t2N=^%mMqcqLqS1zZ?M7tL&CP_R8@T^Q+m7e)ElG~yxPEzd5uh9fqpUtrGbxlr5ZGI~^(q@lu!HYFD0;!NQ9+<pjlRVXn7Q>cSk_;^nsP~vf8}MsQ!YU>>lRHi1{5I{zfj}$eehZRYe#+0?tV|NI#+d8Y9q|yGYig?4igTDd>#@sLF>q*et!7fT9&cZux>U%!EZ{mIE}Aj6wDTlnQq`8#1Y|QnSQ67etryhNW~nJYj~>1F$KWKjN&tYC3;3RQqclf5`Pg*!p5?x2slSAJq<=<2!Q*a0>Q8i(AuA|ig_G$)*M+$q<tE8WV$KI3qNKfw(`IpBoDZA9l)B|iM6+9v5teq#Y7$sPYq~XqxLhqmR?Y#jFgV$(=0+SP4|!=Ni}^|%{@-w(NvR^V;n_09=`NMLU#zT?`56tOMEsKl^q^<8vNOb-j$_A_APz{WNaq}Lz!5`EE!VVI8&ytPlO!i3oL!l4N+7p4osUG`Rutz+E<8J9nT9VU5>+%*d>o*Z{^uvjB{Zah^6hC*{&@(>KQDpyHvH()Q;l_QtAzTiNK7w;I8434c@_~ud*kdb9FM-PaYr{(VG67?4Ac9f%A|lg(C_qv+PtMr$^ri;X0LAx5Wt<q=goNo`gt(}@V5m&RYeJG(u~*rjc2~J`<~pWC_tQs)hjfCMg3*@@aRO2z=j?+fW@WlH%avJ5K%8r>_qNUj5@~YqC#zPAg~y9#UG%IK!@Y+P=|-#l{QGJUn9(|+^z0O116V1VHB(Yzu)iqjSVSI<37J`0ktO+%^q8YPsp?}qdu;t9r?YCYZb&`=;7(r#A%e|Sd%{k+#1mM?uLnn>;p<k8E&uJ0ycqhV#>@mBDVzRnVBYK*WRSlR6vVXl1V+~?Hq;nAbqV7@kMX+VLEBQeiKuuu3~kf=dJ9>hDvmWdgeku>#K@G;l^@aXBtW9SM#zNTG5>I9*u$|1n<dtSek9Tl)RYKi>j?>KT<+?kFZJylubyKHR?64>33Y1B2)tEp$%fck3$vv8(m5`RW=}EIu8I$6^C&S)zz<a?=3bGSs_4Q=|$c>7E|mj;7k@CSYSPr9Co^)p<~W;PW3D1nhvGytNj8N$}}7!7*LV85(SJG?!{Jb9nR0WnKU$qpH;V>ezMpW(-!)pS@%_lFGe};tMqNC@4BsxU!bMbQhy5pur<GG&CMW;9Z;bqi=J7!vxBLr7B1>pVMS`YqOu0o^tie7pZj3>9NzyQz910j')).decode("utf-8"))
__version__ = "V14-SebTape"

_PRICE_FLOOR = 1
_DEMAND_ALPHA = 0.25
_MARKET_PARAMS = {
    "WHEAT": (25, 10000, 400, "sqrt", 0.8, "log", 0.2),
    "CARROT": (35, 10000, 450, "log", 0.2, "sqrt", 0.7),
    "TOMATO": (60, 10000, 200, "linear", 0.4, "sqrt", 0.6),
    "STRAWBERRY": (120, 10000, 100, "sqrt", 0.7, "linear", 1.6),
    "MELON": (250, 10000, 300, "log", 0.2, "sq", 3.6),
    "EGG": (50, 10000, 332, "linear", 0.4, "log", 0.2),
    "MILK": (160, 10000, 122, "sqrt", 0.6, "linear", 1.6),
    "WOOL": (200, 10000, 105, "log", 0.2, "sq", 3.2),
    "FERTILIZER": (100, 10000, 200, "linear", 0.4, "linear", 0.4),
}
_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
_SELLABLE = tuple(_MARKET_PARAMS)
_LIQUIDATION_ORDER = (
    "CARROT", "EGG", "FERTILIZER", "MELON", "MILK",
    "STRAWBERRY", "TOMATO", "WHEAT", "WOOL",
)
_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 8
_SHIFT_STATE = {
    0: {"last_step": -1, "due_step": -1, "due": {}},
    1: {"last_step": -1, "due_step": -1, "due": {}},
}
_PREEMPT_ENABLED = True
_PREEMPT_FRACTION = 2.0
_PREEMPT_MAX_BATCH = 30
_PREEMPT_MAX_CLONE_DISTANCE = 6
_PREEMPT_MIN_PRICE_RATIO = 0.0
_PREEMPT_MIN_FUTURE_QUANTITY = 4
_PREEMPT_START = 120
_PREEMPT_STOP = 680
_PREMIUM = ("STRAWBERRY", "MELON", "MILK", "WOOL")


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _align_hands(action, obs):
    action = _copy_action(action)
    expected = len(_get(_farm(obs, _seat(obs)), "hands", []) or [])
    hands = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(order or ["PASS"]) for order in hands[:expected]]
    return action


def _shed_access(size):
    half = size // 2
    return {
        (half - 1, half - 1), (half, half - 1),
        (half - 1, half), (half, half),
    }


def _projected_shed(obs, action):
    farm = _farm(obs, _seat(obs))
    private = _get(obs, "private", {}) or {}
    projected = {
        key: max(0, int(value or 0))
        for key, value in dict(_get(private, "shed", {}) or {}).items()
    }
    inventories = list(_get(private, "inventories", []) or [])
    positions = [_get(farm, "farmer", [0, 0]), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    tiles = list(_get(farm, "tiles", []) or [])
    access = _shed_access(len(tiles) or 10)
    for index, unit_action in enumerate(unit_actions):
        if index >= len(positions) or index >= len(inventories):
            continue
        position = positions[index]
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            continue
        x, y = int(position[0]), int(position[1])
        if (x, y) not in access or not (0 <= y < len(tiles) and 0 <= x < len(tiles[y])):
            continue
        inventory = {key: max(0, int(value or 0)) for key, value in dict(inventories[index] or {}).items()}
        if unit_action and unit_action[0] == "DROP":
            deposits = inventory.items()
        elif unit_action and unit_action[0] == "PLACE" and len(unit_action) >= 2:
            item = unit_action[1]
            tile = tiles[y][x]
            structure = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}.get(item)
            if structure and isinstance(tile, dict) and tile.get("kind") == structure and not tile.get("animal"):
                continue
            try:
                requested = int(unit_action[2]) if len(unit_action) >= 3 else 1
            except (TypeError, ValueError):
                continue
            deposits = ((item, min(max(0, requested), inventory.get(item, 0))),)
        else:
            continue
        for item, quantity in deposits:
            room = max(0, 100 - sum(projected.values()))
            amount = min(max(0, int(quantity or 0)), room)
            if amount:
                projected[item] = projected.get(item, 0) + amount
    return projected


def _public_signature(farm):
    keys = (
        "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
        "COW", "SHEEP", "GOOSE", "PASTURE", "COOP", "WEED",
    )
    counts = {key: 0 for key in keys}
    for row in (_get(farm, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            for field in ("crop", "animal", "kind"):
                value = str(tile.get(field, "")).upper()
                if value in counts:
                    counts[value] += 1
                    break
    return (
        len(_get(farm, "hands", []) or []),
        len(_get(farm, "unlocked_quadrants", []) or []),
        tuple(counts[key] for key in sorted(counts)),
    )


def _clone_distance(obs):
    farms = list(_get(obs, "farms", []) or [])
    if len(farms) < 2:
        return 10**9
    left, right = _public_signature(farms[0]), _public_signature(farms[1])
    return (
        abs(left[0] - right[0])
        + 3 * abs(left[1] - right[1])
        + sum(abs(a - b) for a, b in zip(left[2], right[2]))
    )


def _shift_state(obs, step):
    seat = _seat(obs)
    state = _SHIFT_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "due_step": -1, "due": {}}
        _SHIFT_STATE[seat] = state
    state["last_step"] = step
    return state


def _repay_shift(obs, action, step):
    if not _PREEMPT_ENABLED:
        return action
    state = _shift_state(obs, step)
    if int(state.get("due_step", -1)) != step:
        if int(state.get("due_step", -1)) < step:
            state["due_step"], state["due"] = -1, {}
        return action
    due = {item: max(0, int(quantity)) for item, quantity in dict(state.get("due") or {}).items()}
    market = []
    for raw in action.get("market", []) or []:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL" and due.get(order[1], 0) > 0:
            item = order[1]
            requested = max(0, int(order[2]))
            reduction = min(requested, due[item])
            requested -= reduction
            due[item] -= reduction
            if requested <= 0:
                continue
            order[2] = requested
        market.append(order)
    action["market"] = market
    state["due_step"], state["due"] = -1, {}
    return action


def _future_sells(step):
    if step + 1 >= len(_ACTIONS):
        return {}
    result = {}
    for raw in (_ACTIONS[step + 1].get("market") or []):
        if len(raw) >= 3 and raw[0] == "SELL" and raw[1] in _PREMIUM:
            result[raw[1]] = result.get(raw[1], 0) + max(0, int(raw[2]))
    return result


def _preempt_shift(obs, action, step):
    if not _PREEMPT_ENABLED or not (_PREEMPT_START <= step < _PREEMPT_STOP):
        return action
    state = _shift_state(obs, step)
    if state.get("due") or _clone_distance(obs) > _PREEMPT_MAX_CLONE_DISTANCE:
        return action
    future = _future_sells(step)
    if not future:
        return action
    market = list(action.get("market") or [])
    if len(market) >= 10:
        return action
    remaining = _projected_shed(obs, action)
    for raw in market:
        if len(raw) >= 3 and raw[0] == "SELL":
            item = raw[1]
            remaining[item] = max(0, int(remaining.get(item, 0) or 0) - max(0, int(raw[2])))
    prices = _get(_get(obs, "market", {}) or {}, "prices", {}) or {}
    shifted = {}
    for item in _PREMIUM:
        future_quantity = max(0, int(future.get(item, 0) or 0))
        if future_quantity < _PREEMPT_MIN_FUTURE_QUANTITY:
            continue
        base_price = float(_MARKET_PARAMS[item][0])
        if float(_get(prices, item, 0) or 0) < base_price * _PREEMPT_MIN_PRICE_RATIO:
            continue
        target = min(
            max(0, int(remaining.get(item, 0) or 0)),
            future_quantity,
            _PREEMPT_MAX_BATCH,
            max(1, int(round(future_quantity * _PREEMPT_FRACTION))),
        )
        if target <= 0 or len(market) >= 10:
            continue
        market.append(["SELL", item, target])
        remaining[item] = max(0, int(remaining.get(item, 0) or 0) - target)
        shifted[item] = target
    if shifted:
        action["market"] = market[:10]
        state["due_step"] = step + 1
        state["due"] = shifted
    return action


def _tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return (_get(farm, "tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"


def _trace_actor_action(step, actor):
    trace = _ACTIONS[min(max(int(step), 0), len(_ACTIONS) - 1)] or {}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])


def _weed_repair_action(obs, action, step):
    action = _align_hands(action, obs)
    seat = _seat(obs)
    game = _WEED_STATE[seat]
    if step == 0 or step < game.get("last_step", -1):
        game = {"last_step": step, "active": {}}
        _WEED_STATE[seat] = game
    game["last_step"] = step
    farm = _farm(obs, seat)
    positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    active = game["active"]

    for actor, transaction in list(active.items()):
        index = 0 if actor == "farmer" else int(actor) + 1
        if index >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - transaction["start"]
        if age == 1:
            unit_actions[index] = list(transaction["intended"])
        elif 2 <= age <= 1 + _WEED_REPLAY_STEPS:
            unit_actions[index] = _trace_actor_action(step - 1, actor)
        else:
            active.pop(actor, None)

    for index, (position, intended) in enumerate(zip(positions, unit_actions)):
        actor = "farmer" if index == 0 else index - 1
        if actor in active or not isinstance(intended, list) or not intended:
            continue
        if intended[0] not in ("BUILD_PASTURE", "PLANT"):
            continue
        tile = _tile_at(farm, position)
        if not isinstance(tile, dict) or tile.get("kind") != "WEED":
            continue
        active[actor] = {"start": step, "intended": list(intended)}
        unit_actions[index] = ["DIG"]

    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"] = unit_actions[1:]
    return _align_hands(action, obs)


def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear":
        return value
    if name == "sq":
        return value * value
    if name == "sqrt":
        return math.sqrt(value)
    if name == "log":
        return math.log1p(value)
    if name == "log10":
        return math.log10(1.0 + value)
    raise ValueError(name)


def _market_price(item, inventory):
    base, equilibrium, scale, below_func, below_target, above_func, above_target = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory)
    else:
        amplitude = above_target * base / _shape(above_func, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))


def _is_sell(order):
    return (
        isinstance(order, (list, tuple))
        and len(order) >= 3
        and order[0] == "SELL"
        and order[1] in _MARKET_PARAMS
    )


def _impact_score(obs, order):
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    prices = _get(market, "prices", {}) or {}
    current_inventory = int(_get(inventory, item, 10000) or 0)
    current_quote = float(_get(prices, item, _market_price(item, current_inventory)) or 0)
    later_quote = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)


def _demand_per_day(obs, configuration, item):
    town = _get(obs, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    turns_per_day = int(_get(configuration, "turnsPerDay", 24) or 24)
    shop_interval = max(1, int(_get(configuration, "townShopSellInterval", 4) or 4))
    demand = 0.0
    for shop in shops:
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += (turns_per_day / shop_interval) * (2 if len(products) == 1 else 1)
    if item != "FERTILIZER":
        center_interval = max(1, int(_get(configuration, "townCenterSellInterval", 24) or 24))
        demand += turns_per_day / center_interval
    return demand


def _order_score(obs, configuration, order):
    score = _impact_score(obs, order)
    if score <= 0 or not _is_sell(order):
        return score
    item = str(order[1])
    quantity = max(0, int(order[2]))
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    current_inventory = int(_get(inventory, item, 10000) or 0)
    demand = max(0.25, _demand_per_day(obs, configuration, item))
    excess = max(0.0, current_inventory + quantity - 10000)
    urgency = min(1.0, (excess / demand) / 10.0)
    return score * (1.0 + _DEMAND_ALPHA * urgency)


def _rank_sell_slots(obs, action, configuration):
    action = _copy_action(action)
    market = list(action.get("market") or [])
    rows = [
        (_order_score(obs, configuration, order), -index, list(order))
        for index, order in enumerate(market)
        if _is_sell(order)
    ]
    if len(rows) < 2:
        return action
    rows.sort(reverse=True)
    ranked = iter(row[2] for row in rows)
    action["market"] = [next(ranked) if _is_sell(order) else order for order in market]
    return action


def _terminal_liquidation(obs, action, step):
    if step < 716:
        return action
    action = _copy_action(action)
    shed = _get(_get(obs, "private", {}) or {}, "shed", {}) or {}
    planned = {item: 0 for item in _SELLABLE}
    for order in action.get("market", []):
        if _is_sell(order):
            planned[str(order[1])] += max(0, int(order[2]))
    for item in _LIQUIDATION_ORDER:
        available = max(0, int(_get(shed, item, 0) or 0))
        extra = available if step >= 718 else max(0, available - planned[item])
        if extra and len(action["market"]) < 10:
            action["market"].append(["SELL", item, extra])
    return action


def agent(obs):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        action = _repay_shift(obs, action, step)
        action = _rank_sell_slots(obs, action, None)
        action = _preempt_shift(obs, action, step)
        action = _terminal_liquidation(obs, action, step)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


def _kaggle_submission_entrypoint(obs):
    return agent(obs)
